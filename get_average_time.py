import os
import numpy as np

IMAGE_SIZE = 10

# 측정값을 저장한 파일들 리스트 추출
def search_records():
    file_list = os.listdir("./result/")
    search_file_list = []
    for file_name in file_list:
        if (file_name.startswith("Gaussian") and file_name.endswith(".txt")):
            search_file_list.append(file_name)
    return search_file_list

def ResultRecord(filename, pic_num, exe_time, check):
	if(check == 0):
		f = open(filename,'w')
		f.write(pic_num + " : " + exe_time + "\n")
	else:
		f = open(filename, 'a')
		f.write(pic_num + " : " + exe_time + "\n")

# IRQ를 사용한 이상치 제거
def remove_out(dataframe, range_const=1.5):
    df = np.array(dataframe)
    # 각 이미지 별로 정렬
    rtn_df = np.sort(df, axis=1)
    rtn = [[]]*10
    for image_index in range(IMAGE_SIZE):   
        q1 = np.quantile(rtn_df[image_index], 0.25)
        q3 = np.quantile(rtn_df[image_index], 0.75)
        
        IRQ = q3 - q1
        lower_bound = q1 - range_const*IRQ
        upper_bound = q3 + range_const*IRQ
        dff = rtn_df[image_index][(rtn_df[image_index] >= lower_bound) & (rtn_df[image_index] <= upper_bound)]
        rtn[image_index]=dff
    return rtn

# 평균 추출
def get_average():
    search_file_list = search_records()
    for file_name in search_file_list:
        f = open('./result/'+file_name, 'r')
        sum_of_processing_time=[0.0]*10
        processed_time=[0]*10
        origin_processed_time = [[]]*10
        while True:
            line = f.readline()
            if not line: break
            data = line.split(" : ")
            image_index = int(data[0])
            processing_time = float(data[1])
            origin_processed_time[image_index]=origin_processed_time[image_index]+[processing_time]
            sum_of_processing_time[image_index] = sum_of_processing_time[image_index]+processing_time
            processed_time[image_index]=processed_time[image_index]+1
        f.close()
        for image_index in range(len(sum_of_processing_time)):
            # Average(filename).txt 에 평균 값 저장
            ResultRecord("./result/Average{0}2.txt".format(file_name[:-4]),str(image_index),
                         str(np.mean(origin_processed_time[image_index])),
                         image_index)
            
            # 이상치 제거(IRQ)
            df = remove_out(origin_processed_time, 1.5)

            # Average(filename)withoutOutLier.txt에 이상치를 제거한 평균 값 저장
            ResultRecord("./result/Average{0}withoutOutLier2.txt".format(file_name[:-4]),str(image_index),
                         str(np.mean(df[image_index])),
                         image_index)

get_average()