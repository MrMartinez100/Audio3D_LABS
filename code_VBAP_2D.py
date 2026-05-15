#!/usr/bin/env python3
import numpy as np
import math
from itertools import combinations

class VBAP_2D_Panner:
    # helper for getting the unit vectors given an polar position in degrees
    def degrees_to_unit_column_vector_2d(input_angle_in_degrees):
        return np.array([ [math.cos(math.radians(input_angle_in_degrees)), math.sin(math.radians(input_angle_in_degrees))] ], dtype=np.float64).transpose()

    # class constructor
    def __init__(self, loudspeakers_azimuth_list_in_degrees):
        # we set an attribute with the loudspeakers unit (column) vectors
        self._loudspeakers_polar_positions_in_degrees = loudspeakers_azimuth_list_in_degrees
        self._loudspeakers_cartesian_2d_positions = [ VBAP_2D_Panner.degrees_to_unit_column_vector_2d(loudspeaker_azimuth_in_degrees) for loudspeaker_azimuth_in_degrees in loudspeakers_azimuth_list_in_degrees ]

    def get_loudspeaker_pair_indexes_for_a_source_location(self, virtual_source_angle_in_degrees):
        """
        Finds the best speaker setup for VBAP given a list of speaker unit vectors and a virtual_source_angle_in_degrees unit vector,
        all in a 2D horizontal plane.
        
        Parameters:
            virtual_source_angle_in_degrees (np.array): A unit vector representing the virtual_source_angle_in_degrees position.
            
        Returns:
            tuple: Best speaker setup .
        """
        best_pair = None
        best_pair_dot_product = -1  # Start with the lowest possible dot product value

        flattened_virtual_source_angle_in_degrees = VBAP_2D_Panner.degrees_to_unit_column_vector_2d(virtual_source_angle_in_degrees).flatten()

        for i, j in combinations(range(len(self._loudspeakers_cartesian_2d_positions)), 2):
        ########################################################################
        ##### COMPLETE HERE ####################################################
            i_dot_source = np.dot(????????????????????????, flattened_virtual_source_angle_in_degrees)
            j_dot_source = np.dot(self._loudspeakers_cartesian_2d_positions[j].flatten(), ??????????????????????????)
        ########################################################################
            dot_product_sum =  i_dot_source + j_dot_source
            if dot_product_sum > best_pair_dot_product:
                best_pair_dot_product = dot_product_sum
                best_pair = (i, j)
    
        return best_pair

    def calculate_2d_vbap_gains(self, 
                                virtual_source_angle_in_degrees,
                                normalization_order = 2,
                                energy_constant = 1.,
                                threshold_angle_for_single_speaker = 1e-5):


        # get the best pair of loudspeakers for the virtual source location 
        best_pair_indexes = self.get_loudspeaker_pair_indexes_for_a_source_location(virtual_source_angle_in_degrees)
        (speaker1_index, speaker2_index) = best_pair_indexes

        # create matrix with those speaker unit vectors
        L12 = np.array([self._loudspeakers_cartesian_2d_positions[speaker1_index],
                        self._loudspeakers_cartesian_2d_positions[speaker2_index]]).reshape(2,2)

        # create the unit vector for the virtual source location
        ########################################################################
        ##### COMPLETE HERE. create the unit vector for the virtual source location. Use VBAP_2D_Panner.degrees_to_unit_column_vector_2d if needed
        p =  ??????????????????????????????????????????
        ########################################################################


        # calculate gains for the PAIR OF SPEAKERS by applying VBAP 2D
        gains = np.matmul(p.transpose(),np.linalg.inv(L12)).flatten()

        # normalize, given normalization_order and energy_constant
        normalization_scale = energy_constant / math.pow(np.sum(gains**normalization_order), 1/normalization_order)
        gains *= normalization_scale 

        # we create an output vector with the number of loudspeaker channels, which we will update and return later
        all_channel_gains = np.zeros(len(self._loudspeakers_cartesian_2d_positions))

        ## check if we have a single loudspeaker or a pair of loudspeakers using the threshold_angle_for_single_speaker
        for i1,i2 in [(0,1), (1,0)]:
            assert gains[i1] <= 1.
            # if the gains are close to 1, we have a single loudspeaker
            # apply normalized gain to it and return
            if 1. - gains[i1] <= threshold_angle_for_single_speaker and gains[i2] <= threshold_angle_for_single_speaker:
                #######################################
                ######## COMPLETE HERE ################
                speaker_index = ?????????????????????????
                #######################################
                all_channel_gains[speaker_index] =  1 # use energy constant and normalization_order (see below on pair of speakers case)
                print(f"Using single speaker {speaker_index} for angle {virtual_source_angle_in_degrees}. all_channel_gains: {all_channel_gains}")
                return all_channel_gains


        #########################################################
        #### COMPLETE HERE (copy calculated gains to the correspondent all_channel_gains elements)
        all_channel_gains[speaker1_index] = ....
        all_channel_gains[speaker2_index] = ....
        #########################################################
        print(f"Using speakers {speaker1_index} and {speaker2_index} for angle {virtual_source_angle_in_degrees}. Gains: {gains}")
        return all_channel_gains

############################################
#### COMPLETE HERE
# create a list with the loudspeakers locations
my_loudspeakers_azimuth_angles_in_degrees = [?????????????]
############################################

# instantiate a Panner object
MyPanner = VBAP_2D_Panner(my_loudspeakers_azimuth_angles_in_degrees)
print(f"Loudspeakers: {my_loudspeakers_azimuth_angles_in_degrees}")

############################################
#### COMPLETE HERE
# print the gains of the asked angles
for angle in ???????????????????:
    print(f"=============================== {angle} ==================================")
    print(f"all_channel_gains: {MyPanner.calculate_2d_vbap_gains(angle)}")
###########################################
