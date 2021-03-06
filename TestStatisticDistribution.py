from itertools import combinations
from math import gcd, sqrt
from fractions import Fraction

from Source import Source
from SamplesXY import SamplesXY
from CountAlgorithm import CountAlgorithm
from CombinedSample import CombinedSample
from Distribution import Distribution


class TestStatisticDistribution:
    def __init__(self, samples_x_y: SamplesXY, shared_combined_sample: CombinedSample):
        self.shared_combined_sample = shared_combined_sample
        self.shared_combined_sample_size = self.shared_combined_sample.combined_sample_size
        self.sample_size_y = samples_x_y.sample_size_y
        self.sample_size_x = self.shared_combined_sample_size - self.sample_size_y
        self.sample_size_x_y_gcd = gcd(self.sample_size_x, self.sample_size_y)
        self.test_statistic_factor = self.sample_size_x * self.sample_size_y / self.sample_size_x_y_gcd
        self.test_statistic_factor_approximate = self.sample_size_x_y_gcd / \
                                 sqrt(self.sample_size_x * self.sample_size_y * self.shared_combined_sample_size)
        self.algorithm = CountAlgorithm()
        self.combined_sample_counts = []
        self.x_meshing_cdf = []
        self.y_meshing_cdf = []
        self.max_cumulative_difference = 0
        self.meshing_test_statistic = 0
        self.y_item_positions = []
        self.number_of_y_item_positions = 0
        self.combined_sample_attributions_cache = []

        self.distribution = Distribution()

    def make_y_item_indices(self):
        print("Calculating meshings... ", sep=" ", end=" ")
        item_indices = [x for x in range(0, self.shared_combined_sample_size)]
        self.y_item_positions = combinations(item_indices, self.sample_size_y)
        self.number_of_y_item_positions = sum(1 for _ in self.y_item_positions)
        # Restore the iterator
        self.y_item_positions = combinations(item_indices, self.sample_size_y)

    def get_y_item_positions(self):
        return self.y_item_positions

    def show_progress(self, step):
        if step % 1000 == 0:
            print("\rCalculating meshings... {}/{}".format(step, self.number_of_y_item_positions), sep=" ", end=" ")

    @staticmethod
    def finish_progress():
        print("\rCalculating meshings... Done")

    def update_combined_sample_attributions(self, y_item_indices):
        next_attributions = [Source.FORM_SAMPLE_X for _ in range(0, self.shared_combined_sample_size)]
        for index in y_item_indices:
            next_attributions[index] = Source.FORM_SAMPLE_Y
        self.shared_combined_sample.set_attributions(next_attributions)

    def make_cdf_from_counts_x(self, count):
        return Fraction(count, self.sample_size_x)

    def make_cdf_from_counts_y(self, count):
        return Fraction(count, self.sample_size_y)

    def save_counts_as_x_meshing_cdf(self):
        self.x_meshing_cdf = map(self.make_cdf_from_counts_x, self.combined_sample_counts)

    def save_counts_as_y_meshing_cdf(self):
        self.y_meshing_cdf = map(self.make_cdf_from_counts_y, self.combined_sample_counts)

    def find_max_cumulative_difference(self):
        cumulative_difference = []
        for index, cumulative_probability_x_y in enumerate(zip(self.x_meshing_cdf, self.y_meshing_cdf)):
            cumulative_difference.append(abs(cumulative_probability_x_y[0] - cumulative_probability_x_y[1]))
        self.max_cumulative_difference = max(cumulative_difference)

    def calculate_test_statistic(self):
        self.meshing_test_statistic = int(self.test_statistic_factor * self.max_cumulative_difference)

    def approximate_test_statistic(self):
        self.meshing_test_statistic = self.test_statistic_factor_approximate * self.meshing_test_statistic

    def append_test_statistic_to_distribution(self):
        self.distribution.add_test_statistic(self.meshing_test_statistic)

    def calculate_meshing_test_statistic(self):
        self.count_x_in_combined_sample()
        self.save_counts_as_x_meshing_cdf()
        self.count_y_in_combined_sample()
        self.save_counts_as_y_meshing_cdf()
        self.find_max_cumulative_difference()
        self.calculate_test_statistic()

    def append_meshing_to_distribution(self):
        self.calculate_meshing_test_statistic()
        self.append_test_statistic_to_distribution()

    def count_x_in_combined_sample(self):
        self.algorithm.configure_count_x()
        self.run_algorithm()

    def count_y_in_combined_sample(self):
        self.algorithm.configure_count_y()
        self.run_algorithm()

    def run_algorithm(self):
        self.shared_combined_sample.run(self.algorithm)
        self.combined_sample_counts = self.algorithm.get_combined_sample_counts()

    def make_probabilities(self):
        self.distribution.calculate_probabilities()

    def make_test_statistic_distribution(self):
        self.make_y_item_indices()
        for index, y_item_indices in enumerate(self.get_y_item_positions()):
            self.show_progress(index)
            self.update_combined_sample_attributions(y_item_indices)
            self.append_meshing_to_distribution()
        self.finish_progress()
        self.make_probabilities()

    def make_test_statistic(self):
        self.calculate_meshing_test_statistic()

    def make_test_statistic_approximate(self):
        self.calculate_meshing_test_statistic()
        self.approximate_test_statistic()

    def cache_attributions(self):
        self.combined_sample_attributions_cache = self.shared_combined_sample.get_attributions_copy()

    def restore_attributions(self):
        self.shared_combined_sample.set_attributions(self.combined_sample_attributions_cache)

    def get_test_statistic(self):
        return self.meshing_test_statistic

    def get_probabilities(self):
        return self.distribution.get_probabilities()

    def get_calculate_p_values_for(self, observed_test_statistic):
        p_value = 0
        for test_statistic, probability in self.get_probabilities().items():
            if test_statistic >= observed_test_statistic:
                p_value += probability
        return p_value

    def perform_test(self):
        # Get the value of the test statistic for the combined samples with the original attributions
        self.make_test_statistic()
        observed_value_of_test_statisitic = self.get_test_statistic()
        self.cache_attributions()

        # Make test statistic distribution
        self.make_test_statistic_distribution()
        p_value = self.get_calculate_p_values_for(observed_value_of_test_statisitic)
        self.restore_attributions()

        print("Observed value of test statistic is {}".format(observed_value_of_test_statisitic))
        print("Exact p-value is {}\n".format(p_value))

    def perform_test_approximate(self):
        self.make_test_statistic_approximate()
        observed_value_of_test_statisitic = self.get_test_statistic()

        print("Observed approximate value of test statistic is {}".format(observed_value_of_test_statisitic))
        print("Critical value for 0.05-rejection region is 1.358\n")
