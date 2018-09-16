#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Я буду мусорить переменными, может потом поправлю :)
'''

import sys
import os
from PIL import Image, ImageDraw
import math
import argparse
import time


def craft_pawn(ImagePath, Background = False):
	
	Source = Image.open(ImagePath)
	SourceWidth, SourceHeight = Source.size

	Color = {} 
	'''
	Пытаемся понять цвет фона,
	предполагаем, что его на картинке больше всего. 
	можно добавить контроль через getpixel по краям изображения,
	но я не настолько хочу заморачиватся. 
	'''
	for x in range(SourceWidth):
		for y in range(SourceHeight):
			pixel = Source.getpixel((x,y))
			
			if pixel in Color:
				Color[pixel] += 1
			else:
				Color[pixel] = 1
	
	MaxPixel = ''
	MaxVal = 0
	for key in Color:
		val = Color[key]
		if val > MaxVal:
			MaxVal = val
			MaxPixel = key
			
			
	print(MaxPixel, MaxVal)
	
	BackPixel = MaxPixel
	'''
	Сейчас, вероятно будет тупой алгоритм, но мне он кажется менее заморочным.
	Делаем несколько проходов, ищем пиковые точки изображения сверху, снизу и сбоков
	пиковые точки должны быть самыми оптимальными и отличными от фона. 
	По итогу, должно получится x1,y1 - x2y2, точки под кроп
	'''

	TopPeak = 0
	TopCoord = SourceHeight
	for x in range(SourceWidth):
		for y in range(SourceHeight):
			current = Source.getpixel((x,y))
			
			# Если мы находим точку, отличной от фона
			if current != BackPixel and y < TopCoord:
				TopPeak = current
				TopCoord = y
				break

	print(TopPeak, TopCoord)
	
	LeftPeak = 0
	LeftCoord = SourceWidth
	for y in range(SourceHeight):
		for x in range(SourceWidth):
			current = Source.getpixel((x,y))	
			
			if current != BackPixel and x < LeftCoord:
				LeftPeak = current
				LeftCoord = x
				break
			
	print(LeftPeak, LeftCoord)
	
	# Нашли пару:
	y1 = TopCoord
	x1 = LeftCoord

	BottomPeak = 0
	BottomCoord = 0
	for x in list(reversed(range(SourceWidth))):
		for y in list(reversed(range(SourceHeight))):
			current = Source.getpixel((x,y))	
			
			if current != BackPixel and y > BottomCoord:
				BottomPeak = current
				BottomCoord = y
				break
				
	print(BottomPeak, BottomCoord)
	
	RightPeak = 0
	RightCoord = 0
	for y in range(SourceHeight):
		for x in range(SourceWidth):
			current = Source.getpixel((x,y))	
			
			if current != BackPixel and x > RightCoord:
				RightPeak = current
				RightCoord = x
				break
			
	print(RightPeak, RightCoord)	
	
	# Вторая пара
	y2 = BottomCoord
	x2 = RightCoord
	
	CropSource = Source.crop((x1, y1, x2, y2))
	
	CropSource = CropSource.convert("RGBA")
	
	
	CropSource = CropSource.rotate(-90, expand=True)
	cw, ch = CropSource.size	
	
	# Если цвет фона не задан, то берем из изображения
	# Есть идея менять фон, но пока не трогаем.
	if Background == False:
		Background = BackPixel
	
	CropTranspone = CropSource.transpose(Image.FLIP_LEFT_RIGHT)
	# крафтим подставку, закруглять пунктиром гимор, кому надо - обрежет
	stand = math.ceil(cw / 4) # размер подставки
	cwa = (cw + stand )*2
	cha = 10 # отступы для линии отреза
	Canvas = Image.new("RGB", (cwa, (cha + ch)), Background)
	Canvas.paste(CropSource, (stand,cha), CropSource)
	Canvas.paste(CropTranspone, (stand+cw,cha), CropTranspone)
	
	crw, crh = Canvas.size
	
	# готовим под края
	Stand_left = stand - 5
	Stand_right = crw - stand + 5

	draw = ImageDraw.Draw(Canvas) 
	draw.line((Stand_left,0, Stand_left,(cha+ch)), fill=12)
	draw.line((Stand_right,0, Stand_right,(cha+ch)), fill=12)
	# Линия отреза
	draw.line((0, math.ceil(cha/2), crw, math.ceil(cha/2)), fill=12)
	
	return Canvas


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser()
	parser.add_argument("-work_dir", help="Директория с изображениями", required=True)
	# parser.add_argument("-repeat", type=int, help="Количество повторений каждого изображения", default=1)
	parser.add_argument("-out", help="Директория сохранения изображений", default="OutImages")
	parser.add_argument("-width", type=int, help="Ширина итогового изображения", default=500)
	
	parser.add_argument("-glue", help="Склеивать в один лист? yes/no", default="no")
       
	args = parser.parse_args()
	
	try:
		os.stat(args.out)
	except:
		os.mkdir(args.out)  
    
	GlueImages = []
	SurfaceHeight = 0
    
	for root, dirs, files in os.walk(args.work_dir):
		for f in files:
			CurrentFile = os.path.join(root, f)
			ext = str(f.split(".")[-1]).lower()
			
			if not os.path.isfile(CurrentFile):
				continue
			
			if ext not in ["png", "jpeg", "jpg", "gif"]:
				continue

			im = craft_pawn(CurrentFile)
			NewFile = os.path.join(args.out, str(int(time.time())))
			
			wpercent = (args.width/float(im.size[0]))
			hsize = int((float(im.size[1])*float(wpercent)))
			im = im.resize((args.width,hsize), Image.ANTIALIAS)
			NewFile = "%s.png" % NewFile
			im.save(NewFile, format="png")
			
			if args.glue == "yes":
				GlueImages.append(NewFile)
				SurfaceHeight += im.size[1]
				
			im.close()
	
	# Я знаю, что это можно сделать в том же цикле, но так нагляднее
	if args.glue == "yes":
		print(SurfaceHeight)
		# пока я не начал делать смену фона, предположу что он белый
		Surface = Image.new("RGBA", (args.width+5, SurfaceHeight+len(GlueImages)*5), (255,255,255))
		print(Surface.size)
		nextPos = 0
		for im in GlueImages:
			img = Image.open(im).convert("RGBA")
			iw, ih = img.size
			print(img.size)
			Surface.paste(img, (0, nextPos+3), img)
			nextPos += ih
			
			
		OutFinal = os.path.join(args.out, "final.png")
		Surface.save(OutFinal, format="png")
			
			
	print("Закончили, хозяин")

	
