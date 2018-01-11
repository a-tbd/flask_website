# artwork information for series

class Series:
	def __init__(self, href, image, alt, caption):
		self.href = href
		self.image = image
		self.alt = alt
		self.caption = caption

	def toJSON(self):
		return {"href":self.href, "image":self.image, "alt":self.alt, "caption":self.caption}
