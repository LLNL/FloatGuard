#include "InstStub.h"
#include <iostream>
#include <fstream>
#include <set>
#include <cstdlib>

int fp_exception_enabled_param = 0;
std::set<long long> saved_rips;
int num_kernel_seq = 0;
int kernel_seq_counter = 0;
long long current_rips[8];
char *current_func[8];

extern "C"
{
    void init_fp_exception_sequence()
    {
        static int first_enter = 0;
        if (!first_enter)
        {
            first_enter = 1;
            for (int i = 0; i < 8; i++)
            {
                current_rips[i] = -1;
                current_func[i] = NULL;
            }
                        
            std::ifstream seq_file;
            seq_file.open("seq.txt");
            if (seq_file.is_open())
            {
                int num_rips;
                seq_file >> num_kernel_seq;
                seq_file >> num_rips;
                //std::cout << num_kernel_seq << "," << num_rips << std::endl;
                for (int i = 0; i < num_rips; i++)
                {
                    std::string rip;
                    seq_file >> rip;
                    //std::cout << strtoll(rip.c_str(), NULL, 16) << std::endl;
                    saved_rips.insert(strtoll(rip.c_str(), NULL, 16));
                }
                seq_file.close();
            }
            else 
            {
                num_kernel_seq = 0x7FFFFFFF;
            }
        }
    }

    int get_fp_exception_enabled(char *func, void *rip)
    {
        for (int i = 8 - 2; i >= 0; i--)
        {
            current_func[i+1] = current_func[i];
            current_rips[i+1] = current_rips[i];
        }
        long long rip_num = (long long)rip;        
        current_func[0] = func;
        current_rips[0] = rip_num;

        kernel_seq_counter++;
        if (kernel_seq_counter > num_kernel_seq)
        {
            if (saved_rips.find(rip_num) != saved_rips.end())
            {
                return 0;
            }
            return 1;
        }
        else
        {
            return 0;
        }
    }
}