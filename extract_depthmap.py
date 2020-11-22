import io
import Image
import photos
import numpy as np
from objc_util import *

class CImage(object):
	def __init__(self, chosen_pic_data):
		CIImage = ObjCClass('CIImage')
		options = {}
		options['kCIImageAuxiliaryDepth'] = ns(True)
		options['kCIImageApplyOrientationProperty'] = ns(True)
		self.ci_img = CIImage.imageWithData_options_(chosen_pic_data, options)
	
	def to_png(self):
		ctx = ObjCClass('CIContext').context()
		try:
			extent = self.ci_img.extent()
		except:
			print('The selected portrait photo does not contain depth information.')
			quit()
		m = ctx.outputImageMaximumSize()
		cg_img = ctx.createCGImage_fromRect_(self.ci_img, extent)
		ui_img = UIImage.imageWithCGImage_(cg_img)
		png_data = uiimage_to_png(ObjCInstance(ui_img))
		return png_data

for album in photos.get_smart_albums():
	if album.title == "Portrait":
		my_album = album
		break

try:
	chosen_pic = photos.pick_asset(assets = my_album.assets, title = 'Select a portrait photo')
	chosen_pic_image = chosen_pic.get_image(original = True)
	chosen_pic_data = chosen_pic.get_image_data(original = True).getvalue()
	chosen_pic_depth = CImage(ns(chosen_pic_data)).to_png()
	chosen_pic_depth_stream = io.BytesIO(chosen_pic_depth)
	chosen_pic_depth_image = Image.open(chosen_pic_depth_stream)
	chosen_pic_image = chosen_pic_image.resize(chosen_pic_depth_image.size, Image.ANTIALIAS)
	
	
	# This part makes sure that the whole 0-255 range is utilized in the depth map. Might or might not be useful to you.
	x = np.array(chosen_pic_depth_image).astype(int)
	if np.ptp(x) == 0: # Some Portrait photos have a completely white depth map. Let's treat those as if there was no depth map at all.
		print('The selected portrait photo does not contain a depth map.')
		quit()
	x = (255*(x - np.min(x))/np.ptp(x)).astype(int)
	chosen_pic_depth_image_normalized = Image.fromarray(np.uint8(x))
	
	print('Filename: ' + str(ObjCInstance(chosen_pic).originalFilename()))
	print('Date taken: ' + str(chosen_pic.creation_date))
	chosen_pic_image.show()
	chosen_pic_depth_image.show()
	chosen_pic_depth_image_normalized.show()
except Exception as e:
	print(e)
	pass
