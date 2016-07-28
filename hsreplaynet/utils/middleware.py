
class DoNotTrackMiddleware:
	HEADER = "HTTP_DNT"

	def process_request(self, request):
		if self.HEADER in request.META:
			request.dnt = request.META[self.HEADER] == "1"
		else:
			request.dnt = None

	def process_response(self, request, response):
		if self.HEADER in request.META:
			response["DNT"] = request.META[self.HEADER]
		return response
