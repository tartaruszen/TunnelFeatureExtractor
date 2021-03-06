from scapy.all import *

from PcapFeatures import PcapFeatures
from CapLibrary import CapLibrary

import logging
import errno
# import csv
import json

class TunnelFeatureExtractorJSON(object):

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.INFO)
        # self.logger.setLevel(logging.WARNING)
        self.logger.debug("Testing debug message")
        #print("Passed logging message")

        self.capLib = CapLibrary()

    def make_sure_path_exists(self, path):
        try:
            os.makedirs(path)
            print("Path Created: ", path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def test_feature_extraction(self):
        # # Either: ==> Test first pcap
        path_list = self.capLib.get_paths_from_specific_lib_in_pcap_base('HTTPovDNS')
        self.logger.debug('First Path: %s ' % str(path_list[0]).strip())
        pcap_feat = PcapFeatures(str(path_list[2]).strip(), 'HTTP')
        lens_seq = pcap_feat.getDnsReqLens()
        self.logger.debug("Packet Length List-len: %i" % len(lens_seq))
        self.logger.debug("First Pkt Length: %i" % lens_seq[0])
        self.logger.debug("Second Pkt Length: %i" % lens_seq[1])
        #pcap_feat.test_pkt_Reader()
        pcap_feat.doPlot(lens_seq, 'red', 'DNS Req Entropy', 'Pkt #', 'Entropy')

        # # or: ==> Test multiple pcaps
        # for count, single_file_path in enumerate(self.capLib.get_paths_from_specific_lib_in_pcap_base('HTTPovDNS')):
        #     self.logger.debug("Pcap File Path #: %i" % count)
        #     pcap_feat = PcapFeatures(single_file_path, 'HTTPovDNS')
        #     lens_seq = pcap_feat.getDnsReqLens()
        #
        #     self.logger.debug("Req Len seq len: %i" % len(lens_seq))
        #
        #     pcap_feat.doPlot(lens_seq, 'r', 'DNS Req Entropy', 'Pkt #', 'Entropy')

    def get_feature_vectors_and_write_to_file(self, protoLabel, featureName):
        # Check if directory exists (i.e. feature_base, and sub directory of HTTPovDNS / FTPovDNS)
        self.make_sure_path_exists("feature_base/JSON/" + protoLabel+ "/" + featureName)

        # curr_feature_filename = ""
        # # Check if file exists
        # if featureName == "DNS-Req-Lens":
        #     curr_feature_filename = "DNS_Layer_Req_Lengths.csv"
        # elif featureName == "IP-Req-Lens":
        #     curr_feature_filename = "IP_Layer_Req_Lengths.csv"
        # elif featureName == "DNS-Req-Qnames":
        #     curr_feature_filename = "DNS_Layer_Req_Query_names.csv"

        # curr_feature_filePath = "feature_base/JSON/" + protoLabel + "/" + curr_feature_filename
        curr_feature_filePath = "feature_base/JSON/" + protoLabel + "/" + featureName + '/' + featureName + '.json'

        curr_pcap_file_name = 'Not yet set.'
        try:
            with open(curr_feature_filePath, mode='w') as json_feature_file:
                feature_vect_list = None
                json_obj_list = []
                for count, single_file_path in enumerate(self.capLib.get_paths_from_specific_lib_in_pcap_base(protoLabel)):
                    self.logger.debug("Pcap File Path #: %i" % count)
                    curr_pcap_file_name = str(single_file_path).rsplit('/', 1)[1].strip()
                    self.logger.debug("Current PCAP File name: %s" % curr_pcap_file_name)
                    pcap_feat = PcapFeatures(single_file_path, protoLabel)

                    #Choose the Feature to be extracted
                    if featureName == "DNS-Req-Lens":
                        feature_vect_list = pcap_feat.getDnsReqLens()
                    elif featureName == "IP-Req-Lens":
                        feature_vect_list = pcap_feat.get_ip_pkt_lengths()
                    elif featureName == "DNS-Req-Qnames-Enc-Comp-Hex":
                        feature_vect_list = pcap_feat.getDnsReqQnames_upstream()
                    # HTTP Related Features
                    elif featureName == "HTTP-Req-Bytes-Hex":
                        feature_vect_list = pcap_feat.getHttpReqBytesHex()

                    self.logger.debug("Req Len seq len: %i" % len(feature_vect_list))

                    self.logger.debug("Populating feature vector from PCAP [%s]" % (curr_pcap_file_name))
                    #Add PCAP file name as primary key (at the head of the list)
                    # feature_vect_row = [pcapFilename] + feature_vect_list      #<==== Also works but stackoverflow says code below is faster
                    #feature_vect_list.insert(0, curr_pcap_file_name)

                    #vect_csv_writer = csv.writer(csv_feature_file, delimiter=',')

                    # writerow takes a list i.e. []
                    # vect_csv_writer.writerow(feature_vect_row)
                    #vect_csv_writer.writerow(feature_vect_list)
                    json_obj_str = {'filename': curr_pcap_file_name,
                               'pcap-Md5-hash': '',
                               'protocol': protoLabel,
                               'props': {'feature-name': featureName,
                                         'values': feature_vect_list}}
                    # Ideally for the values i'd need square brackets [], but since it's a list it is recognized

                    # Add each json_obj_str from an individual pcap file into a list containing all specific features in json format
                    json_obj_list.append(json_obj_str)
                # Encode the list into a single file containing features of each pcap (comma separated for each pcap)
                json.dump(json_obj_list, json_feature_file, indent=4, sort_keys=True)

        except IOError:
            self.logger.debug("File IOError ... with: %s : %s" % (featureName, curr_pcap_file_name))

            #self.write_feature_vector_instance_to_file(feat_vect_seq, protoLabel, curr_pcap_file_name)
        # return feat_vect_seq


featureExt = TunnelFeatureExtractorJSON()
#featureExt.test_feature_extraction()

#featureExt.write_feature_vector_instance_to_file(featureExt.get_feature_vectors("HTTPovDNS"), "HTTPovDNS")

# featureExt.get_feature_vectors_and_write_to_file("HTTPovDNS", "DNS-Req-Lens")      # <---- Works
# featureExt.get_feature_vectors_and_write_to_file("HTTPovDNS", "IP-Req-Lens")       # <---- Works
# featureExt.get_feature_vectors_and_write_to_file("HTTPovDNS", "DNS-Req-Qnames-Enc-Comp-Hex")

#featureExt.get_feature_vectors_and_write_to_file("HTTP-Plain", "HTTP-Req-Bytes-Hex")
featureExt.get_feature_vectors_and_write_to_file("HTTP-ovDNS-v-Plain-SIZE", "DNS-Req-Qnames-Enc-Comp-Hex")