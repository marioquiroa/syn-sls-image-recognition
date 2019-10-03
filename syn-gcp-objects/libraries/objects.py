from libraries.gcp_service import gcp_service 

class objects:
	
	logger = -1
	object_list = []

	def __init__(self,logger,event):
		self.logger = logger.global_log
		service = gcp_service(event)
		self.logger.info('GCP call')
		self.process_objects(service.get_response())
		
	def process_objects(self,result):
		self.logger.info('Formatting objects')
		for i, obj in enumerate(result.annotation_results[0].object_annotations):
			if(len(obj.entity.description)>0):
				appearance_list = self.all_appearances(obj.segment.start_time_offset,obj.frames,obj.confidence)
				self.all_objects(obj.entity.description,appearance_list)

	def all_appearances(self,initial_time,all_frames,confidence):
		appearance_list = []
		previous_milliseconds = self.milliseconds(initial_time)
		for current_frame in all_frames:
			current_milliseconds = self.milliseconds(current_frame.time_offset)
			appearance_dict = self.one_appearance(current_frame.normalized_bounding_box,
				previous_milliseconds,current_milliseconds,confidence)
			appearance_list.append(appearance_dict)
			previous_milliseconds = current_milliseconds
		return appearance_list

	def milliseconds(self,time):
		milliseconds = str(round((time.seconds + time.nanos/1e9)*1000,4))
		return milliseconds

	def one_appearance(self,box,previous_milliseconds,current_milliseconds,confidence):
		appearance_dict = {}
		appearance_dict["left"] = round(box.left,4)
		appearance_dict["top"] = round(box.top,4)
		appearance_dict["right"] = round(box.right,4)
		appearance_dict["bottom"] = round(box.bottom,4)
		appearance_dict["start"] = previous_milliseconds
		appearance_dict["end"] = current_milliseconds
		appearance_dict["confidence"] = round(confidence,4)
		return appearance_dict		

	def all_objects(self,object_name,appearance_list):
		exist = self.check_existence(object_name)
		if exist:
			self.already_on_list(object_name,appearance_list)
		else:
			self.new_on_list(object_name,appearance_list)

	def check_existence(self,name):
		exist = False
		for element in self.object_list: 
			if(element['object']==name):
				exist = True
				break;	
		return exist

	def already_on_list(self,name,appearance_list):
		for element in self.object_list: 
			if(element['object']==name):
				element['appearances'] += appearance_list
				break;

	def new_on_list(self,name,appearance_list):
		object_dict = {}
		object_dict["object"] = name
		object_dict["appearances"] = appearance_list
		self.object_list.append(object_dict)

	def get_json(self):
		return self.object_list