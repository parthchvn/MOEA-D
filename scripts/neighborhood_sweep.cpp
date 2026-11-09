// Cyclic own-parent MOEA/D with one shared observation per offspring.
// All stopping times use sweep boundaries. No genotype-specific information is
// needed: both operators sample new weights from the parent's Hamming weight.
#include <algorithm>
#include <charconv>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using Count = std::uint64_t;
using Weights = std::vector<int>;

template <class T> T integer(const std::string& text) {
    T value{};
    const char* last = text.data() + text.size();
    auto parsed = std::from_chars(text.data(), last, value);
    if (parsed.ec != std::errc{} || parsed.ptr != last)
        throw std::invalid_argument("invalid integer: " + text);
    return value;
}

void require(bool ok, const char* message) {
    if (!ok) throw std::invalid_argument(message);
}

std::string choice(const std::string& input, const char* a, const char* b) {
    if (input != a && input != b)
        throw std::invalid_argument("expected " + std::string(a) + " or " + b);
    return input;
}

double real(const std::string& text) {
    std::size_t used = 0;
    double value = std::stod(text, &used);
    require(used == text.size() && std::isfinite(value), "invalid finite number");
    return value;
}

void check_dimensions(int n, int T) {
    require(n >= 2 && n < std::numeric_limits<int>::max() - 1, "n outside supported range");
    require(1 <= T && T <= n + 1, "T must be between 1 and n+1");
}

Weights weights_csv(const std::string& text, int n) {
    Weights values;
    std::size_t pos = 0;
    while (true) {
        auto comma = text.find(',', pos);
        int w = integer<int>(text.substr(pos, comma - pos));
        require(w >= 0 && w <= n, "weight outside [0,n]");
        values.push_back(w);
        if (comma == std::string::npos) break;
        pos = comma + 1;
    }
    require(values.size() == static_cast<std::size_t>(n + 1), "expected n+1 weights");
    return values;
}

// The set chosen by sim.build_neighborhoods is contiguous. The odd/even
// breeder tie break determines the extra side for even T. At endpoints the
// interval slides inward to keep its cardinality exactly T.
int first_recipient(int n, int T, int breeder) {
    const int left = (T - 1) / 2 + (T % 2 == 0 && breeder % 2 == 1);
    return std::clamp(breeder - left, 0, n + 1 - T);
}

void print_neighbors(int n, int T, int breeder) {
    require(breeder >= 0 && breeder <= n, "invalid breeder");
    const int first = first_recipient(n, T, breeder), last = first + T - 1;
    std::cout << '[' << breeder;
    const int direction = breeder % 2 == 0 ? 1 : -1;
    for (int d = 1; d <= std::max(breeder-first, last-breeder); ++d) {
        for (int sign : {direction, -direction}) {
            const std::int64_t k = static_cast<std::int64_t>(breeder) + sign * d;
            if (first <= k && k <= last) std::cout << ',' << k;
        }
    }
    std::cout << "]\n";
}

// All compared labels lie between the updated extremes. Multiplication by n
// removes scalarization denominators. Ties are accepted.
std::int64_t cost(int n, int target, int label, int lo, int hi) {
    return std::max(std::int64_t(target) * (hi-label),
                    std::int64_t(n-target) * (label-lo));
}

struct Population {
    int n, T;
    Weights weights, stored;
    int lo, hi;
    int pinned_labels = 0;
    Count comparisons = 0, external_replacements = 0, external_changes = 0;
    Count endpoint_repairs_own = 0, endpoint_repairs_external = 0;
    int first_zero_donor = -1;

    Population(int n_, int T_, Weights w, Weights b, int lo_, int hi_)
        : n(n_), T(T_), weights(std::move(w)), stored(std::move(b)), lo(lo_), hi(hi_) {
        require(0 <= lo && lo <= hi && hi <= n, "invalid extrema");
        for (int k = 0; k <= n; ++k) {
            require(lo <= stored[k] && stored[k] <= hi, "extrema must enclose stored labels");
            pinned_labels += stored[k] == k;
        }
    }

    bool ideal() const { return lo == 0 && hi == n; }
    bool all_pinned() const { return ideal() && pinned_labels == n + 1; }

    void replace(int k, int breeder, int child, int obs) {
        // Count from this endpoint's individual pin, which may precede S.
        if ((k == 0 || k == n) && ideal() && stored[k] == k && weights[k] != k && child == k) {
            if (k == breeder) ++endpoint_repairs_own;
            else ++endpoint_repairs_external;
            if (k == 0 && first_zero_donor < 0) first_zero_donor = breeder;
        }
        if (k != breeder) {
            ++external_replacements;
            external_changes += weights[k] != child || stored[k] != obs;
        }
        pinned_labels += int(obs == k) - int(stored[k] == k);
        weights[k] = child;
        stored[k] = obs;
    }

    void advance(int breeder, int child, int obs) {
        lo = std::min(lo, obs);
        hi = std::max(hi, obs);
        const int first = first_recipient(n, T, breeder), last = first + T - 1;
        comparisons += T;
        // At the ideal reference every pinned slot accepts only its target.
        // All receivers share one candidate, hence at most slot obs accepts.
        if (all_pinned()) {
            if (first <= obs && obs <= last) replace(obs, breeder, child, obs);
            return;
        }
        for (int k = first; k <= last; ++k) {
            if (cost(n, k, obs, lo, hi) <= cost(n, k, stored[k], lo, hi))
                replace(k, breeder, child, obs);
        }
    }
};

struct RandomWeights {
    std::mt19937_64 rng;
    std::uniform_int_distribution<int> bit_index;
    std::bernoulli_distribution active;
    std::vector<std::binomial_distribution<int>> flips;
    int n;
    double p;
    bool mutation_one, noise_one;

    RandomWeights(int n_, double p_, Count seed, bool m1, bool z1)
        : rng(seed), bit_index(0, n_-1), active(p_), n(n_), p(p_),
          mutation_one(m1), noise_one(z1) {
        flips.reserve(n+1);
        for (int total=0; total<=n; ++total) flips.emplace_back(total, 1.0/n);
    }

    int round(int w, bool one) {
        if (one) return bit_index(rng) < w ? w-1 : w+1;
        // Draw sequentially, in specified order, so compiler expression
        // evaluation order cannot change the trajectory.
        const int removed = flips[w](rng);
        const int added = flips[n-w](rng);
        return w - removed + added;
    }

    int observe(int w) {
        return p > 0.0 && active(rng) ? round(w, noise_one) : w;
    }
};

struct Events {
    // -1 denotes a right-censored (not yet observed) boundary.
    std::int64_t exact = -1, front = -1, archive = -1, U = -1, S = -1, post = -1;
    int bad_U = -1, bad_S = -1, max_error_U = -1, max_error_S = -1;
    Weights last_seen;
    std::vector<unsigned char> archived;
    int archived_count = 0;

    explicit Events(int n) : last_seen(n+1, -1), archived(n+1, 0) {}

    void generated(int w) {
        if (!archived[w]) { archived[w] = 1; ++archived_count; }
    }

    void boundary(const Population& pop, std::int64_t t) {
        bool now_exact = true;
        int bad = 0, max_error = 0, distinct = 0;
        // Clear the scratch bitmap once per boundary; no randomness is used.
        if (front < 0) std::fill(last_seen.begin(), last_seen.end(), 0);
        for (int k=0; k<=pop.n; ++k) {
            int w = pop.weights[k], err = std::abs(w-pop.stored[k]);
            now_exact = now_exact && w == k;
            bad += err != 0;
            max_error = std::max(max_error, err);
            if (front < 0 && !last_seen[w]) { last_seen[w] = 1; ++distinct; }
        }
        if (exact < 0 && now_exact) exact = t;
        if (front < 0 && distinct == pop.n+1) front = t;
        if (archive < 0 && archived_count == pop.n+1) archive = t;
        if (U < 0 && pop.ideal()) { U = t; bad_U = bad; max_error_U = max_error; }
        if (S < 0 && pop.all_pinned()) { S = t; bad_S = bad; max_error_S = max_error; }
        if (post < 0 && S >= 0 && now_exact) post = t;
    }
};

void number_or_null(std::int64_t x) {
    if (x < 0) std::cout << "null"; else std::cout << x;
}

void print_weights(const Weights& weights) {
    std::cout << '[';
    for (std::size_t i=0; i<weights.size(); ++i) {
        if (i) std::cout << ',';
        std::cout << weights[i];
    }
    std::cout << ']';
}

void simulation(int n, int T, double factor, Count seed, std::int64_t cap,
                bool mutation_one, bool noise_one, bool corner, bool ideal) {
    require(0 <= factor && factor <= n, "factor/n must be in [0,1]");
    require(cap >= 0, "negative sweep cap");
    require(!corner || ideal, "supplied corner requires ideal reference");
    require(static_cast<Count>(cap) <= std::numeric_limits<Count>::max() / (n+1) / T,
            "comparison counter would overflow");
    RandomWeights random(n, factor/n, seed, mutation_one, noise_one);
    Weights w(n+1), b(n+1);
    if (corner) {
        std::iota(w.begin(), w.end(), 0);
        b = w;
        w[0] = 2;
    } else {
        std::binomial_distribution<int> uniform(n, 0.5);
        for (auto& value : w) value = uniform(random.rng);
        for (int k=0; k<=n; ++k) b[k] = random.observe(w[k]);
    }
    int lo = ideal ? 0 : *std::min_element(b.begin(), b.end());
    int hi = ideal ? n : *std::max_element(b.begin(), b.end());
    Population pop(n, T, std::move(w), std::move(b), lo, hi);
    Events events(n);
    for (int weight : pop.weights) events.generated(weight);
    std::int64_t sweep = 0;
    events.boundary(pop, sweep);
    while (sweep < cap && events.post < 0) {
        for (int breeder=0; breeder<=n; ++breeder) {
            const int child = random.round(pop.weights[breeder], mutation_one);
            const int observed = random.observe(child);
            events.generated(child);
            pop.advance(breeder, child, observed);
        }
        events.boundary(pop, ++sweep);
    }
    std::cout << "{\"sweeps\":" << sweep
              << ",\"attempts\":" << Count(sweep) * (n+1)
              << ",\"init_evals\":" << (corner ? 0 : n+1)
              << ",\"comparisons\":" << pop.comparisons
              << ",\"external_replacements\":" << pop.external_replacements
              << ",\"external_changes\":" << pop.external_changes;
    auto field = [](const char* key, std::int64_t value) {
        std::cout << ",\"" << key << "\":";
        number_or_null(value);
    };
    field("exact_sweep", events.exact);
    field("front_sweep", events.front);
    field("archive_sweep", events.archive);
    field("U", events.U);
    field("S", events.S);
    field("post_sweep", events.post);
    field("bad_at_U", events.bad_U);
    field("max_error_at_U", events.max_error_U);
    field("bad_at_S", events.bad_S);
    field("max_error_at_S", events.max_error_S);
    field("first_corner_donor", corner ? pop.first_zero_donor : -1);
    std::cout << ",\"endpoint_repairs_own\":" << pop.endpoint_repairs_own
              << ",\"endpoint_repairs_external\":" << pop.endpoint_repairs_external;
    std::cout << "}\n";
}

void sample(int n, int parent, double factor, Count seed, Count draws, bool mutation_one,
            bool noise_one) {
    require(n >= 2 && n <= 512 && parent >= 0 && parent <= n,
            "sample requires n in [2,512] and a valid parent weight");
    require(0 <= factor && factor <= n && draws > 0, "invalid factor or draws");
    RandomWeights random(n, factor/n, seed, mutation_one, noise_one);
    std::vector<std::vector<Count>> counts(n+1, std::vector<Count>(n+1));
    for (Count t=0; t<draws; ++t) {
        const int child = random.round(parent, mutation_one);
        ++counts[child][random.observe(child)];
    }
    std::cout << '[';
    for (int j=0; j<=n; ++j) {
        if (j) std::cout << ',';
        std::cout << '[';
        for (int b=0; b<=n; ++b) {
            if (b) std::cout << ',';
            std::cout << counts[j][b];
        }
        std::cout << ']';
    }
    std::cout << "]\n";
}

} // namespace

int main(int argc, char** argv) {
    try {
        const std::string mode = argc > 1 ? argv[1] : "";
        if (mode == "neighbors") {
            require(argc == 5, "usage: engine neighbors n T breeder");
            int n = integer<int>(argv[2]), T = integer<int>(argv[3]);
            check_dimensions(n,T);
            print_neighbors(n, T, integer<int>(argv[4]));
        } else if (mode == "sample") {
            require(argc == 9, "usage: engine sample n parent factor seed draws mutation noise");
            sample(integer<int>(argv[2]),integer<int>(argv[3]),real(argv[4]),
                   integer<Count>(argv[5]),integer<Count>(argv[6]),
                   choice(argv[7],"one","bit")=="one", choice(argv[8],"one","bit")=="one");
        } else if (mode == "step") {
            require(argc == 11, "usage: engine step n T breeder true,weights stored,weights lo hi child obs");
            int n = integer<int>(argv[2]), T = integer<int>(argv[3]);
            check_dimensions(n,T);
            int breeder = integer<int>(argv[4]);
            require(breeder >= 0 && breeder <= n, "invalid breeder");
            int child = integer<int>(argv[9]), obs = integer<int>(argv[10]);
            require(child >= 0 && child <= n && obs >= 0 && obs <= n, "invalid offspring");
            Population pop(n,T,weights_csv(argv[5],n),weights_csv(argv[6],n),
                           integer<int>(argv[7]),integer<int>(argv[8]));
            pop.advance(breeder,child,obs);
            std::cout << "{\"true\":"; print_weights(pop.weights);
            std::cout << ",\"stored\":"; print_weights(pop.stored);
            std::cout << ",\"lo\":" << pop.lo << ",\"hi\":" << pop.hi << "}\n";
        } else {
            require(argc == 10, "usage: engine n T factor seed max_sweeps mutation noise init reference");
            int n = integer<int>(argv[1]), T = integer<int>(argv[2]);
            check_dimensions(n,T);
            simulation(n,T,real(argv[3]),integer<Count>(argv[4]),integer<std::int64_t>(argv[5]),
                       choice(argv[6],"one","bit")=="one", choice(argv[7],"one","bit")=="one",
                       choice(argv[8],"uniform","corner")=="corner",
                       choice(argv[9],"observed","ideal")=="ideal");
        }
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return EXIT_FAILURE;
    }
}
