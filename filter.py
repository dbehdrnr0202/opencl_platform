import pyopencl as cl #OpenCL을 파이썬 상에서 사용하기 위한 라이브러리
from PIL import Image #이미지 입출력을 위한 라이브러리
import numpy as np #이미지 문자열 변환을 위한 라이브러리
import time
import argparse

def process_arg():
	parser = argparse.ArgumentParser(description="Pixel per WORK ITEM")
	# platform 번호(NVIDIA CUDA, Intel OpenCL, AMD)
	parser.add_argument('--p', type=int, help="Platform index")
	# 워크그룹 설정
	parser.add_argument('--w', type=int, help="Pixel per WORK ITEM")
	# 처리 이미지 설정
	parser.add_argument('--i', type=int, help='Processing image index')
	# 처리한 이미지 저장 설정
	parser.add_argument('--s', type=int, default=0, help='Save proccessed image option')
	
	return parser

PIXEL_PER_WORK_ITEM = 1 #2,4,8,16,32
#문맥 생성
def CreateContext(platform_index):
	#사용 가능한 플랫폼 탐색
	platforms = cl.get_platforms()
	if len(platforms) == 0:
		print("OpenCL을 실행할 수 있는 플랫폼이 존재하지 않습니다.")
		return None
	
	select_platform_num = platform_index

	#해당 플랫폼에서 사용될 디바이스 선택
	devices = platforms[int(select_platform_num)].get_devices(cl.device_type.ALL)
	if len(devices) == 0:
		print("사용할 수 있는 디바이스가 없습니다.")
		return None
	'''
	else:
		print("사용될 디바이스 정보")
		print(devices[0])
		print('디바이스 메모리 크기 : ' + str(int(devices[0].get_info(cl.device_info.GLOBAL_MEM_SIZE)/1000000000)) + 'GB')
		print('디바이스 전역 캐시 크기 : ' + str(devices[0].get_info(cl.device_info.GLOBAL_MEM_CACHE_SIZE)) + 'BYTE')
		print('디바이스 최대 작업-그룹 크기 : ' + str(devices[0].get_info(cl.device_info.MAX_WORK_GROUP_SIZE)))
	'''

	#실제 문맥 생성 (첫 번째 디바이스를 활용 (CUDA의 경우 GPU / Intel OpenCL의 경우 CPU 디바이스가 잡힘))
	context = cl.Context([devices[0]])

	#생성된 문맥과 디바이스를 반환함
	return context, devices[0]
	
# OpenCL 프로그램 생성 (커널 파일 사용)
def CreateProgram(context, device, filename):
	kernelFile = open(filename, 'r')
	kernelStr = kernelFile.read()
	
	# 커널 내 작성된 코드 읽어옴
	program = cl.Program(context, kernelStr)
	
	# 커널 내 작성된 코드를 빌드하고, 에러 검출 시 출력함
	program.build(devices=[device])
	
	return program
	
# Python Image Library를 활용하여 실험에 사용하고자 하는 이미지 불러오기
def LoadImage(context, image_num):

	select_picture_num = image_num
	im = Image.open('./origin_images/'+select_picture_num+'.jpg')
	
	# 이미지를 R/G/B/A 4채널의 모드가 되도록 확실하게 설정
	if im.mode != "RGBA":
		im = im.convert("RGBA")
	
	# numpy 라이브러리를 활용하여 이미지를 string으로 변환함
	buffer = np.asarray(im)
	print("이미지 변환 성공")

	clImageFormat = cl.ImageFormat(cl.channel_order.RGBA, cl.channel_type.UNORM_INT8)
	
	clImage = cl.Image(context,
						cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
						clImageFormat,
						im.size,
						None,
						buffer
						)
	
	print("이미지 처리 성공")

	return clImage, im.size, select_picture_num
	
# Python Image Library를 사용하여 string으로 저장된 buffer를 이미지로 재변환하여 결과를 저장 (실제 필터링은 거친 결과)
def SaveImage(filename,buffer,imgSize):
	im = Image.frombytes("RGBA", imgSize, buffer.tobytes())
	im.save(filename)
	
# 그룹-사이즈를 유사하게 만들어줌
def RoundUp(groupSize, globalSize):
	r = globalSize % groupSize
	if r == 0:
		return globalSize
	else:
		return globalSize + groupSize - r

def ResultRecord(filename, pic_num, exe_time, check):
	if(check == 0):
		f = open(filename,'w')
		f.write(pic_num + " : " + exe_time + "\n")
	else:
		f = open(filename, 'a')
		f.write(pic_num + " : " + exe_time + "\n")

import math

def main():
	imageObjects = [0, 0]
	parser = process_arg()
	parse_config = parser.parse_args()
	#문맥을 생성하고 디바이스를 선택합니다.
	PIXEL_PER_WORK_ITEM= int(math.pow(2, int(parse_config.w)))
	#print("PIXEL_PER_WORK_ITEM: ", PIXEL_PER_WORK_ITEM, "w: ", parse_config.w, 2^int(parse_config.w))
	context, device = CreateContext(parse_config.p)
	if context == None:
		print("OpenCL 문맥 생성에 실패했습니다.")
		return 1
		
	# 생성된 문맥과 선택한 디바이스를 가지고 명령-큐를 만들어냅니다.
	commandQueue = cl.CommandQueue(context, device)
	
	# 사용하고자 하는 디바이스가 이미지 처리를 지원하는지 점검합니다.
	if not device.get_info(cl.device_info.IMAGE_SUPPORT):
		print("현재 사용 중인 디바이스는 이미지 처리를 지원하지 않습니다") 
		return 1
		
	# 이미지 파일을 불러오고, 해당 이미지 파일을 OpenCL 이미지 객체로 변환합니다.
	imageObjects[0], imgSize, select_picture_num = LoadImage(context, str(parse_config.i))
	
	# 출력 이미지 객체를 생성합니다.
	clImageFormat = cl.ImageFormat(cl.channel_order.RGBA, cl.channel_type.UNORM_INT8)
	imageObjects[1] = cl.Image(context, cl.mem_flags.WRITE_ONLY, clImageFormat, imgSize)
	
	# 이미지 객체에 대한 샘플링 객체 생성. 샘플링 객체는 필터링/주소/이미지를 읽는 좌표 모드 명세
	sampler = cl.Sampler(context,
							False,
							cl.addressing_mode.CLAMP_TO_EDGE,
							cl.filter_mode.LINEAR)	
				
	# 커널 파일을 불러오고 프로그램 생성
	program = CreateProgram(context, device, "GaussianFilter2D.cl")

	# 커널 호출
	localWorkSize = (PIXEL_PER_WORK_ITEM,PIXEL_PER_WORK_ITEM)
	globalWorkSize = (RoundUp(localWorkSize[0], imgSize[0]),RoundUp(localWorkSize[1], imgSize[1]))

	time_start = time.time()
	program.gaussian_filter(commandQueue,
							globalWorkSize,
							localWorkSize,
							imageObjects[0],
							imageObjects[1],
							sampler,
							np.int32(imgSize[0]),
							np.int32(imgSize[1]))

	# 호스트로부터 출력 버퍼를 읽어와 이미지 객체 저장
	buffer = np.zeros(imgSize[0] * imgSize[1] * 4, np.uint8)
	origin = (0, 0, 0)
	region = (imgSize[0], imgSize[1], 1)
	cl._enqueue_read_image(commandQueue, imageObjects[1], origin, region, buffer).wait()
	time_end = time.time()

	print('커널 수행이 완료된 시간          : {}'.format(time_end-time_start))
	print("정상적으로 실험이 종료되었습니다.")
	# 변환된 이미지를 저장함
	if parse_config.s==1 and parse_config.w==0:
		SaveImage("./result_images/"+select_picture_num+".png",buffer, imgSize)

	ResultRecord("./result/Gaussian({0})(size{1}).txt".format(device.get_info(cl.device_info.NAME), PIXEL_PER_WORK_ITEM*PIXEL_PER_WORK_ITEM),str(select_picture_num),str(time_end-time_start),select_picture_num)

main()
