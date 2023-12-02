#!/bin/bash
WORK_GROUP_MAX_EXP=6
IMAGE_SIZE=10

#n번 실행시킬 param
n=$1
echo "$n execute n times"

array=$(python find_platform.py)
# 여기서 있는 플랫폼을 찾고, 디바이스 정보를 platform_device_info.json으로 저장(NVIDIA CUDA or Intel(R) OpenCL)
# find_platform.py의 find_platform line13에서 위의 CUDA, OpenCL 말고 있을 경우 추가하기
# 나온 결과의 platform index를 array에 저장
for p in $array; 
    do
    for (( w=0; w < $WORK_GROUP_MAX_EXP; w++)) 
    #        2^0(1), 2^1(2), 2^2(4), 2^3(8), 2^4(16), 2^5(32)
    # size는 1,      4,      16,     64,     256,     1024
    do
        for ((i=0; i < $IMAGE_SIZE; i++))
        do
# 18-22는 주석처리됨
: <<"END"
            echo "platform_index: $p"
            echo "work_group: $w"
            echo "image_index: $i"
END
            python filter.py --p $p --w $w --i $i --s $s
        done
    done
done
