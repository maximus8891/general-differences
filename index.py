from SamplesXY import SamplesXY
from CombineAlgorithm import CombineAlgorithm
from TestStatisticDistribution import TestStatisticDistribution

if __name__ == '__main__':
    algorithm_instance = CombineAlgorithm()

    # Example 1
    # samples_x_y_instance = SamplesXY(sample_x=[1], sample_y=[2, 3, 4])

    # Example 2
    # samples_x_y_instance = SamplesXY(sample_x=[5, 10], sample_y=[2, 2, 10])

    # Example 3
    samples_x_y_instance = SamplesXY(sample_x=[11, 12, 13, 14],
                                     sample_y=[5, 6, 7])

    # Combine the two samples into one, noting the samples the values came from
    samples_x_y_instance.run(algorithm_instance)
    combined_sample_instance = algorithm_instance.get_combined_sample()

    distribution = TestStatisticDistribution(samples_x_y=samples_x_y_instance,
                                             shared_combined_sample=combined_sample_instance)

    distribution.perform_test()
    distribution.perform_test_approximate()
