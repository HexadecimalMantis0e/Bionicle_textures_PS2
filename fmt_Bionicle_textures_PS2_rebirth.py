#######################################################################################
# Bionicle: the Game PS2 texture import script by maver1k_XVII and Hexadecimal Mantis #
#######################################################################################

from inc_noesis import *
import noesis
import rapi
import struct
import os
import io

def registerNoesisTypes():
   handle = noesis.register("Bionicle: the Game images", ".bin")
   noesis.setHandlerTypeCheck(handle, noepyCheckType)
   noesis.setHandlerLoadRGBA(handle, Bio1LoadRGBA)
   noesis.logPopup()
   return 1

# check if it's this type based on the data
def noepyCheckType(data):
	return 1

def Bio1LoadRGBA(data, texList):
	textcount = 1
	bs = NoeBitStream(data)
	filesize = bs.getSize()
	filesizeDiv4 = filesize//4
	for i in range(0, filesizeDiv4-1):
		Temp = bs.readInt()
		
		# Texture headers
		
		if (Temp == 0x004F61C8) or (Temp == 0x004F8288) or (Temp == 0x004F5110) or (Temp == 0x004F9260) or (Temp == 0x004FD320) or (Temp == 0x004FF504) or (Temp == 0x004F7218) or (Temp == 0x00543B28) or (Temp == 0x004F8298) or (Temp == 0x004F8280) or (Temp == 0x004F92D0):
			offset = bs.tell()
			bs.seek(0x09, NOESEEK_REL)
			palPosition = bs.readByte()
			bitDepth = bs.readByte()
			bs.seek(0x19, NOESEEK_REL)
			off2pal = bs.readInt()
			bs.seek(0xC, NOESEEK_REL)
			width = bs.readInt()
			height = bs.readInt()
			if (width > 2048) or (height > 2048):
				continue
			print (textcount)

			print('Found a texture at {0}, width - {1}, height - {2}'.format(hex(offset - 0x4), width, height))
			textcount+=1
			bs.seek(0x30, NOESEEK_REL)
			off2raw = bs.tell()
			bs.seek(off2pal, NOESEEK_ABS)
			print('Found a palette at {0}'.format(hex(off2pal)))
			bs.seek(0x50, NOESEEK_REL)
			palSize = 0x400
			pal = bs.readBytes(palSize)
			
			f0 = io.BytesIO(pal)
			f1 = io.BytesIO(pal)
			count = 0
			swapCount = 0
			block0 = []
			block1 = []
			
			# Unswizzle palette block
			
			while count != 0x100:
                              color = struct.unpack('i', f0.read(4))[0]
                              f1.write(struct.pack("i", color))
                              count += 1
                              swapCount += 1

                              if count == 8 or swapCount == 16:
                                    for i in range(0,8):
                                       color = struct.unpack('i', f0.read(4))[0]
                                       block0+=[color]

                                    for i in range(0,8):
                                       color = struct.unpack('i', f0.read(4))[0]
                                       block1+=[color]

                                    for i in range(0,8):
                                       f1.write(struct.pack("i", block1[i]))

                                    for i in range(0,8):
                                       f1.write(struct.pack("i", block0[i]))

                                    block0=[]
                                    block1=[]

                                    count += 16
                                    swapCount = 0
                                    
			f1.seek(0x00, io.SEEK_SET)
			
			# Seek to correct palette in palette block if texture has a bit depth of 4
			# Else, read the whole palette block
			
			if bitDepth == 0x14:
                           newpalPosition = palPosition * 0x40
                           f1.seek(newpalPosition, io.SEEK_SET)
                           thepal = f1.read(0x40)
                           
			else:
			   thepal = f1.read()
			   
			newpal = bytearray(thepal)
			bs.seek(off2raw, NOESEEK_ABS)

			# 0x14: 16 color palette, 0x13: 256 palette, 0x00: No palette
			
			if bitDepth == 0x14:
			    img = rapi.imageDecodeRawPal(bs.readBytes(width*height), newpal, width, height, 4, "r8g8b8a8")
			if bitDepth == 0x13:
			    img = rapi.imageDecodeRawPal(bs.readBytes(width*height), newpal, width, height, 8, "r8g8b8a8")
			if bitDepth == 0x00:
			    img = rapi.imageDecodeRaw(bs.readBytes(width*height*4), width, height, "r8g8b8a8")
			    
			texList.append(NoeTexture(str(i), width, height, img, noesis.NOESISTEX_RGBA32))
			bs.seek(offset, NOESEEK_ABS)

		# Texture package headers
		
		if (Temp == 0x004F5124) or (Temp == 0x004F92E4) or (Temp == 0x004F722C) or (Temp == 0x004FF518):
			offset = bs.tell()
			bs.seek(0x09, NOESEEK_REL)
			palPosition = bs.readByte()
			bitDepth = bs.readByte()
			bs.seek(0x05, NOESEEK_REL)
			off2pal = bs.readInt()
			bs.seek(0x20, NOESEEK_REL)
			numTex = bs.readShort()
			print('Found a texture package at {0}, number of textures - {1}'.format(hex(offset - 0x4), numTex))
			bs.seek(0x2, NOESEEK_REL)
			off2inf = bs.readInt()
			bs.seek(off2inf, NOESEEK_ABS)
			for j in range(0, numTex):
				bs.seek(0x8, NOESEEK_REL)
				width = bs.readInt()
				height = bs.readInt()
				off2tex = bs.readInt()
				bs.seek(0x4, NOESEEK_REL)
				
				print (textcount)
				
				print('Found a texture at {0}, width - {1}, height - {2}'.format(hex(off2tex), width, height))
				textcount+=1

				bs.seek(off2pal, NOESEEK_ABS)
				print('Found a palette at {0}'.format(hex(off2pal)))
				bs.seek(0x50, NOESEEK_REL)
				palSize = 0x400
				pal = bs.readBytes(palSize)
				f0 = io.BytesIO(pal)
				
				f1 = io.BytesIO(pal)
				count = 0
				swapCount = 0
				block0 = []
				block1 = []
				
				# Unswizzle palette block
				
				while count != 0x100:
                                      color = struct.unpack('i', f0.read(4))[0]
                                      f1.write(struct.pack("i", color))
                                      count += 1
                                      swapCount += 1

                                      if count == 8 or swapCount == 16:
                                            for i in range(0,8):
                                                color = struct.unpack('i', f0.read(4))[0]
                                                block0+=[color]

                                            for i in range(0,8):
                                                color = struct.unpack('i', f0.read(4))[0]
                                                block1+=[color]

                                            for i in range(0,8):
                                                f1.write(struct.pack("i", block1[i]))

                                            for i in range(0,8):
                                                f1.write(struct.pack("i", block0[i]))

                                            block0=[]
                                            block1=[]

                                            count += 16
                                            swapCount = 0
                                    
				f1.seek(0x00, io.SEEK_SET)

				# Seek to correct palette in palette block if texture has a bit depth of 4
				# Else, read the whole palette block

				if bitDepth == 0x14:
                                   newpalPosition = palPosition * 0x40
                                   f1.seek(newpalPosition, io.SEEK_SET)
                                   thepal = f1.read(0x40)
                           
				else:
                                   thepal = f1.read()
			   
				newpal = bytearray(thepal)
				bs.seek(off2tex + 0x20, NOESEEK_ABS)
				
				# 0x14: 16 color palette, 0x13: 256 palette, 0x00: No palette
				
				if bitDepth == 0x14:
                                  img = rapi.imageDecodeRawPal(bs.readBytes(width*height), newpal, width, height, 4, "r8g8b8a8")  
				if bitDepth == 0x13:
                                  img = rapi.imageDecodeRawPal(bs.readBytes(width*height), newpal, width, height, 8, "r8g8b8a8")
				if bitDepth == 0x00:
                                  img = rapi.imageDecodeRaw(bs.readBytes(width*height*4), width, height, "r8g8b8a8")

				texList.append(NoeTexture(str(i+j), width, height, img, noesis.NOESISTEX_RGBA32))

				bs.seek(off2inf + (j + 1)*0x18, NOESEEK_ABS)
			bs.seek(offset, NOESEEK_ABS)
	return 1
