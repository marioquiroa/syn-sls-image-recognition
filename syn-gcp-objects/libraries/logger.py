import logging

class logger:
	
	global_log = -1

	def __init__(self, aws_request_id):
		self.global_log = logging.getLogger()
		self.global_log.setLevel(logging.INFO)
		self.global_log.handlers[0].setFormatter(
			logging.Formatter('[{}] %(levelname)s %(message)s \n'
				.format(aws_request_id)
			)
		)