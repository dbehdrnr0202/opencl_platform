import pyopencl as cl #OpenCL을 파이썬 상에서 사용하기 위한 라이브러리

def find_platform():
    platforms = cl.get_platforms()
    if len(platforms) == 0:
        #print("OpenCL을 실행할 수 있는 플랫폼이 존재하지 않습니다.")
        return None
    platform_num_info=[]
    platform_list = ['NVIDIA CUDA', 'Intel(R) OpenCL', 'AMD Accelerated Parallel Processing']
	#실험 시 플랫폼 설정을 위한 메뉴
    for i in range(len(platforms)):
        platform_name = platforms[i].get_info(cl.platform_info.NAME)
        #print(platform_name)
        if (platform_name in platform_list):
            platform_num_info.append(i)
    #select_platform_num = input("사용하고자 하는 플랫폼을 설정하세요 : ")

	#해당 플랫폼에서 사용될 디바이스 선택
    device_info={}
    device_info['data']=[]
    for i in range(len(platform_num_info)):
        devices = platforms[int(platform_num_info[i])].get_devices(cl.device_type.ALL)
    
        if len(devices) == 0:
            print("사용할 수 있는 디바이스가 없습니다.")
        else:	
            '''
            print("사용될 디바이스 정보")
            print(devices[0])
            print('디바이스 메모리 크기 : ' + str(int(devices[0].get_info(cl.device_info.GLOBAL_MEM_SIZE)/1000000000)) + 'GB')
            print('디바이스 전역 캐시 크기 : ' + str(devices[0].get_info(cl.device_info.GLOBAL_MEM_CACHE_SIZE)) + 'BYTE')
            print('디바이스 최대 작업-그룹 크기 : ' + str(devices[0].get_info(cl.device_info.MAX_WORK_GROUP_SIZE)))
            '''
            print(platform_num_info[i])
            device_info['data'].append({"platform_number":platform_num_info[i],
                                "platform_info":platforms[int(platform_num_info[i])].get_info(cl.platform_info.NAME),
                                "device_name":str(devices[0]), 
                                "device_memory":str(int(devices[0].get_info(cl.device_info.GLOBAL_MEM_SIZE)/1000000000)) + 'GB', 
                                "device_gloval_memory_cache":str(devices[0].get_info(cl.device_info.GLOBAL_MEM_CACHE_SIZE)) + 'BYTE', 
                                "device_max_work_group_size":str(devices[0].get_info(cl.device_info.MAX_WORK_GROUP_SIZE))})
    return platform_num_info, device_info

import os
import json
def record_infos(filename, to_write):
    with open(filename, 'w') as f:
        json.dump(to_write, f, indent=4)

		
def main():
    platform_num_info, platform_device_info = find_platform()
    if platform_num_info==[]:
        return 1
    else:
        #record_infos("platform_device_info.json", platform_device_info)
        return 0

main()