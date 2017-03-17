# -*- coding: utf-8 -*-
from PySide.QtCore import *
from PySide.QtGui import *
from Noriter.UI import Widget as nWidget
from command.FontManager import FontManager

class TimelineKeyFrameArea(QWidget):
	def __init__(self,timeline,parent=None):
		super(TimelineKeyFrameArea,self).__init__(parent)

		self.pressedFrame = -1
		self.pressedNode = -1
		self.pressingFrame = -1

		self.pressedPoint = None
		self.pressingPoint = None
		self.selectedKeyFrames = []

		self.timeline=timeline

	def paintEvent(self, e):
		qp = QPainter(self)
		qp.setFont(FontManager().FontName("NanumBarunGothic"))

		frameFieldWidth = self.timeline.frameFieldWidth
		nodeFieldHeight = self.timeline.nodeFieldHeight
		keyFrameEllipseDiameter = self.timeline.keyFrameEllipseDiameter

		keyFrameBrush = QBrush(QColor(70,100,100))

		pressedFrameBrush = QBrush(QColor(255,140,140))
		pressingFrameBrush = QBrush(QColor(100,100,255))

		noBrush = QBrush(Qt.NoBrush)

		highlightingBrush = QBrush(QColor(70,70,40))

		normalPen = QPen(QColor(85,85,85))
		normalPen.setStyle(Qt.DotLine)
		qp.setPen(normalPen)

		affPen = QPen(QColor(140,140,140))
		affPen.setStyle(Qt.DashLine)

		keyFramePen = QPen(QColor(140,200,200))
		keyFramePen.setStyle(Qt.SolidLine)

		whitePen = QPen(QColor(255,255,255))

		noPen = QPen(Qt.NoPen)

		currentFrameCount = self.timeline.currentFrameCount
		currentNodeCount = self.timeline.currentNodeCount

		frameLimit = self.timeline.maxFrameAddition + 10
		if currentFrameCount < frameLimit:
			currentFrameCount = frameLimit

		xoffset = self.geometry().left()
		yoffset = self.geometry().top()
		geoWidth = self.timeline._scroll.geometry().width()
		geoHeight = self.timeline._scroll.geometry().height()

		i = (-yoffset / nodeFieldHeight) - 1
		while (i * nodeFieldHeight) <= (-yoffset + geoHeight):
			if i < 0:
				i = i + 1
				continue
			if i >= currentNodeCount:
				break

			if len(self.timeline._data[i]) > 0:			
				#background highlighting
				qp.setPen(noPen)
				qp.setBrush(highlightingBrush)
				startFrame = self.timeline._data[i]["frames"][0][0]
				endFrame = self.timeline._data[i]["frames"][-1][0]

				startXCoor = frameFieldWidth * startFrame
				endXCoor = frameFieldWidth * (endFrame + 1)
				if startXCoor < -xoffset:
					startXCoor = -xoffset
				if endXCoor > -xoffset + geoWidth:
					endXCoor = -xoffset + geoWidth
				qp.drawRect(startXCoor,nodeFieldHeight*i,endXCoor-startXCoor,nodeFieldHeight)
		
			# draw holizontal line
			qp.setPen(normalPen)
			lineStart = QPoint(-xoffset,nodeFieldHeight*(i+1))
			lineEnd = QPoint(-xoffset+geoWidth,nodeFieldHeight*(i+1))
			qp.drawLine(lineStart,lineEnd)
			r=keyFrameEllipseDiameter/2

			# for drawing "SELECTING" point
			if self.pressingPoint != None:
				startNodeIndex = self.pressedPoint.y()/self.timeline.nodeFieldHeight
				endNodeIndex = self.pressingPoint.y()/self.timeline.nodeFieldHeight
				startFrameIndex = self.pressedPoint.x()/self.timeline.frameFieldWidth
				endFrameIndex = self.pressingPoint.x()/self.timeline.frameFieldWidth

				if startNodeIndex > endNodeIndex:
					startNodeIndex, endNodeIndex = endNodeIndex, startNodeIndex
				if startFrameIndex > endFrameIndex:
					startFrameIndex, endFrameIndex = endFrameIndex, startFrameIndex

			qp.setPen(keyFramePen)
			for frame,data in self.timeline._data[i]["frames"]:
				frameCenterPoint = QPoint(frameFieldWidth*frame+frameFieldWidth/2,nodeFieldHeight*(i)+nodeFieldHeight/2)
				if (frameCenterPoint.x() + r >= -xoffset) and (frameCenterPoint.x() - r <= -xoffset + geoWidth):
					qp.setBrush(keyFrameBrush)

					if self.pressingPoint != None:
						# if dragging for select
						if i >= startNodeIndex and i <= endNodeIndex:
							if frame >= startFrameIndex and frame <= endFrameIndex:
								qp.setBrush(pressedFrameBrush)

					qp.drawEllipse(frameCenterPoint,r,r)

					if len(data) > 1:
						# multidata in keyframe then, draw "+" icon
						qp.setPen(whitePen)
						qp.drawLine(frameCenterPoint.x()-2,frameCenterPoint.y(),frameCenterPoint.x()+2,frameCenterPoint.y())
						qp.drawLine(frameCenterPoint.x(),frameCenterPoint.y()-2,frameCenterPoint.x(),frameCenterPoint.y()+2)
						qp.setPen(keyFramePen)

			i = i + 1

		i = (-xoffset / frameFieldWidth) - 1
		while (i * frameFieldWidth) <= (-xoffset + geoWidth):
			if i < 0:
				i = i + 1
				continue
			if i >= currentFrameCount:
				break

			# draw vertical line
			if i % 5 == 0:
				qp.setPen(affPen)
			else:
				qp.setPen(normalPen)

			lineStart = QPoint(frameFieldWidth*(i+1),-yoffset)
			targetYPoint = nodeFieldHeight*currentNodeCount
			if targetYPoint > -yoffset+geoHeight:
				targetYPoint = -yoffset+geoHeight
			lineEnd = QPoint(frameFieldWidth*(i+1),targetYPoint)
			qp.drawLine(lineStart,lineEnd)

			i = i + 1


		if len(self.selectedKeyFrames) > 0:
			# if exist selected keyframes
			qp.setPen(keyFramePen)
			qp.setBrush(pressedFrameBrush)
			r=keyFrameEllipseDiameter/2
			for n, f, d in self.selectedKeyFrames:
				frameCenterPoint = QPoint(frameFieldWidth*f+frameFieldWidth/2,nodeFieldHeight*n+nodeFieldHeight/2)
				qp.drawEllipse(frameCenterPoint,r,r)

				if len(d) > 1:
					# multidata in keyframe then, draw "+" icon
					qp.setPen(whitePen)
					qp.drawLine(frameCenterPoint.x()-2,frameCenterPoint.y(),frameCenterPoint.x()+2,frameCenterPoint.y())
					qp.drawLine(frameCenterPoint.x(),frameCenterPoint.y()-2,frameCenterPoint.x(),frameCenterPoint.y()+2)
					qp.setPen(keyFramePen)	

		if self.pressedNode != -1:
			qp.setPen(keyFramePen)	
			qp.setBrush(pressedFrameBrush)

			frameCenterPoint = QPoint(frameFieldWidth*self.pressedFrame+frameFieldWidth/2,nodeFieldHeight*self.pressedNode+nodeFieldHeight/2)
			qp.drawEllipse(frameCenterPoint,keyFrameEllipseDiameter/2,keyFrameEllipseDiameter/2)

			if self.pressingFrame != -1:
				qp.setBrush(pressingFrameBrush)

				if len(self.selectedKeyFrames) < 1:
					frameCenterPoint = QPoint(frameFieldWidth*self.pressingFrame+frameFieldWidth/2,nodeFieldHeight*self.pressedNode+nodeFieldHeight/2)
					qp.drawEllipse(frameCenterPoint,keyFrameEllipseDiameter/2,keyFrameEllipseDiameter/2)
				else:
					offset = self.pressingFrame - self.pressedFrame

					r=keyFrameEllipseDiameter/2

					for n, f, d in self.selectedKeyFrames:
						frameCenterPoint = QPoint(frameFieldWidth*(f+offset)+frameFieldWidth/2,nodeFieldHeight*n+nodeFieldHeight/2)
						qp.drawEllipse(frameCenterPoint,r,r)

		if self.pressingPoint != None:
			qp.setPen(whitePen)
			qp.setBrush(noBrush)
			qp.drawRect(self.pressedPoint.x(),self.pressedPoint.y(),self.pressingPoint.x()-self.pressedPoint.x(),self.pressingPoint.y()-self.pressedPoint.y())


	def mousePressEvent(self,event):
		pressedFrame = event.x()/self.timeline.frameFieldWidth
		pressedNode = event.y()/self.timeline.nodeFieldHeight
		btn = self.timeline.getMouseButton(event.button())

		if pressedNode < 0:
			pressedNode = 0
		if pressedNode >= len(self.timeline._data):
			pressedNode = len(self.timeline._data) - 1

		targetDatas = self.timeline._data[pressedNode]["frames"]
		targetFrame = None

		if btn == "L":
			for f, d in targetDatas:
				if f == pressedFrame:
					targetFrame = f
					break

			if targetFrame != None:
				isSelectedKeyFrame = False

				if len(self.selectedKeyFrames) > 0:
					for n, f, d in self.selectedKeyFrames:
						if n == pressedNode and f == pressedFrame:
							isSelectedKeyFrame = True
							break

					if isSelectedKeyFrame:
						#Multiple select=start keyframe move
						#No special action
						pass

					else:
						self.selectedKeyFrames = []

				#Single select=start keyframe move
				self.pressedFrame = pressedFrame
				self.pressedNode = pressedNode
			else:
				#Multi select=select start
				self.selectedKeyFrames = []
				self.pressedPoint = QPoint(event.x(),event.y())

		self.repaint()

		super(TimelineKeyFrameArea,self).mousePressEvent(event)

	def mouseMoveEvent(self,event):
		pressingFrame = event.x()/self.timeline.frameFieldWidth
		pressingNode = event.y()/self.timeline.nodeFieldHeight

		if pressingFrame < 0:
			pressingFrame = 0

		if self.pressedFrame != -1:
			#Single select=moving keyframe

			if len(self.selectedKeyFrames) > 0:
				#Multiple select=moving keyframe
				offset = pressingFrame - self.pressedFrame

				minoffset = 0

				for n, f, d in self.selectedKeyFrames:
					nextFrame = offset + f

					if minoffset > nextFrame:
						minoffset = nextFrame

				if minoffset < 0:
					pressingFrame = pressingFrame - minoffset

			self.pressingFrame = pressingFrame
			self.timeline.maxFrameAddition = pressingFrame

			frameFieldWidth = self.timeline.frameFieldWidth
			nodeFieldHeight = self.timeline.nodeFieldHeight

			frameCenterPoint = QPoint(frameFieldWidth*self.pressingFrame+frameFieldWidth/2,nodeFieldHeight*self.pressedNode+nodeFieldHeight/2)
			self.timeline._scroll.ensureVisible(frameCenterPoint.x(),frameCenterPoint.y(),frameFieldWidth*2,0)
		elif self.pressedPoint != None:
			#Multi select=selecting
			geom = self.geometry()
			self.pressingPoint = QPoint(event.x(),event.y())

			if self.pressingPoint.x() < 0:
				self.pressingPoint = QPoint(0,self.pressingPoint.y())
			if self.pressingPoint.y() < 0:
				self.pressingPoint = QPoint(self.pressingPoint.x(),0)
			if self.pressingPoint.x() >= geom.width():
				self.pressingPoint = QPoint(geom.width()-1, self.pressingPoint.y())
			if self.pressingPoint.y() >= geom.height():
				self.pressingPoint = QPoint(self.pressingPoint.x(),geom.height()-1)

			frameFieldWidth = self.timeline.frameFieldWidth

			self.timeline._scroll.ensureVisible(self.pressingPoint.x(),self.pressingPoint.y(),frameFieldWidth,frameFieldWidth)



		self.timeline.update()

		super(TimelineKeyFrameArea,self).mouseMoveEvent(event)

	def mouseReleaseEvent(self,event):
		releaseFrame = event.x()/self.timeline.frameFieldWidth
		releaseNode = event.y()/self.timeline.nodeFieldHeight
		btn = self.timeline.getMouseButton(event.button())

		if releaseFrame < 0:
			releaseFrame = 0

		if btn == "L":
			if self.pressedFrame != -1:
				if len(self.selectedKeyFrames) > 0:
					#Multiple select=moving keyframe
					offset = releaseFrame - self.pressedFrame

					minoffset = 0

					for n, f, d in self.selectedKeyFrames:
						nextFrame = offset + f

						if minoffset > nextFrame:
							minoffset = nextFrame

					offset = offset - minoffset

					movingDataContainer = []

					#self.selectedKeyFrames 는 노드, 프레임 순서로 정렬되어있다
					#먼저 데이터를 지운다
					currentNode = 0
					currentFrame = 0

					for n, f, d in self.selectedKeyFrames:
						if currentNode != n:
							currentNode = n
							currentFrame = 0

						while self.timeline._data[currentNode]["frames"][currentFrame][0] < f:
							currentFrame = currentFrame + 1

						if self.timeline._data[currentNode]["frames"][currentFrame][0] != f:
							print "Invalid select keyframe information"
							continue

						self.timeline._data[currentNode]["frames"].pop(currentFrame)

					#다음, 데이터를 다시 넣는다
					nextKeyFrames = []
					for n, f, d in self.selectedKeyFrames:
						self.timeline._data[n]["frames"].append((f + offset, d))
						nextKeyFrames.append((n, f+offset, d))
					self.selectedKeyFrames = nextKeyFrames

				else:
					#Single select=finish move keyframe
					targetDatas = self.timeline._data[self.pressedNode]["frames"]
					for data in targetDatas:
						if data[0] == self.pressedFrame:
							metaData = data[1]
							targetDatas.remove(data)
							targetDatas.append((releaseFrame,metaData))
							break

				self.timeline.update()
				self.timeline.changed.emit()

			elif self.pressedPoint != None:
				#Multi select=select finish
				self.selectedKeyFrames = []

				startNodeIndex = self.pressedPoint.y()/self.timeline.nodeFieldHeight
				endNodeIndex = releaseNode
				startFrameIndex = self.pressedPoint.x()/self.timeline.frameFieldWidth
				endFrameIndex = releaseFrame

				if endNodeIndex >= len(self.timeline._data):
					endNodeIndex = len(self.timeline._data) - 1

				if startNodeIndex > endNodeIndex:
					startNodeIndex, endNodeIndex = endNodeIndex, startNodeIndex
				if startFrameIndex > endFrameIndex:
					startFrameIndex, endFrameIndex = endFrameIndex, startFrameIndex				

				for i in range(startNodeIndex, endNodeIndex+1):
					for f, d in self.timeline._data[i]["frames"]:
						if f >= startFrameIndex and f <= endFrameIndex:
							self.selectedKeyFrames.append((i,f,d))

			self.pressedFrame = -1
			self.pressedNode = -1
			self.pressingFrame = -1
			self.timeline.maxFrameAddition = 0
			self.pressedPoint = None
			self.pressingPoint = None

		self.repaint()

		super(TimelineKeyFrameArea,self).mouseReleaseEvent(event)

	def moveEvent(self, e):
		self.timeline.repaint()
		return super(TimelineKeyFrameArea,self).moveEvent(e)

class Timeline(QWidget):
	#signal
	changed = Signal()

	def __init__(self,data=None,parent=None):
		super(Timeline,self).__init__(parent)

		self._data = data
		self.currentFrameCount = 101
		self.currentNodeCount = 10
		self.maxFrameAddition = 0

		self._scroll = QScrollArea(self)
		self.timelineKeyFrameArea = TimelineKeyFrameArea(self,self)

		self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self._scroll.setWidgetResizable(True)
		self._scroll.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

		self._scroll.setWidget(self.timelineKeyFrameArea)

		contentlayout = QVBoxLayout(self)
		contentlayout.addWidget(self._scroll)
		self.setLayout(contentlayout)

		self.nodeFieldWidth = 100
		self.frameFieldWidth = 13

		self.timeFieldHeight = 40
		self.nodeFieldHeight = 19

		self.keyFrameEllipseDiameter = 9
		self.pressedNode = -1

		contentlayout.setContentsMargins(self.nodeFieldWidth-1, self.timeFieldHeight-1, 0, 0)
		contentlayout.setSpacing(0)

		self.update()

	@property
	def data(self):
		return self._data

	@data.setter
	def data(self, value):
		self._data = value
		self.update()

	def update(self):
		nextMaxFrame = self.maxFrameAddition
		for node in self._data:
			node["frames"] = sorted(node["frames"], key=lambda data: data[0]) # sort by frame

			if nextMaxFrame < node["frames"][-1][0]:
				nextMaxFrame = node["frames"][-1][0]

			nodeFrames = node["frames"]
			if len(nodeFrames) > 1:
				i = 1
				while i < len(nodeFrames):
					if nodeFrames[i-1][0] == nodeFrames[i][0]:
						nextData = (nodeFrames[i-1][0],nodeFrames[i-1][1] + nodeFrames[i][1])
						nodeFrames.remove(nodeFrames[i])
						nodeFrames.remove(nodeFrames[i-1])
						nodeFrames.insert(i-1,nextData)
						i = i - 1
					i = i + 1

		self.currentFrameCount = nextMaxFrame + 100
		self.currentNodeCount = len(self._data)

		self.timelineKeyFrameArea.setFixedWidth(self.currentFrameCount*self.frameFieldWidth)
		self.timelineKeyFrameArea.setFixedHeight(len(self._data)*self.nodeFieldHeight)

		# print "update() called. self._data=",self._data

		self.repaint()

	def paintEvent(self, e):
		qp = QPainter(self)
		qp.setFont(FontManager().FontName("NanumBarunGothic"))

		frameAreaGeometry = self.timelineKeyFrameArea.geometry()
		xoffset = frameAreaGeometry.x()
		yoffset = frameAreaGeometry.y()

		defaultNodeBrush = QBrush(QColor(90,50,50))
		pressedNodeBrush = QBrush(QColor(50,50,120))
		qp.setBrush(defaultNodeBrush)
		textPen = QPen(QColor(222,177,177))
		qp.setPen(textPen)

		frameLimit = self.maxFrameAddition + 10
		if frameLimit < self.currentFrameCount:
			frameLimit = self.currentFrameCount

		geoWidth = self._scroll.geometry().width()
		geoHeight = self._scroll.geometry().height()

		i = (-xoffset / self.frameFieldWidth) - 1
		while (i * self.frameFieldWidth) <= (-xoffset + geoWidth):
			if i < 0:
				i = i + 1
				continue
			if i >= frameLimit:
				break

			boundingBox=QRect(xoffset+self.nodeFieldWidth+self.frameFieldWidth*i,0,self.frameFieldWidth,self.timeFieldHeight-1)
			wordBoundingBox=QRect(-self.timeFieldHeight,xoffset+self.nodeFieldWidth+self.frameFieldWidth*i+2,self.timeFieldHeight,self.frameFieldWidth)
			qp.drawRect(boundingBox)
			qp.save()
			qp.rotate(-90)
			qp.drawText(wordBoundingBox,Qt.AlignCenter,str(i))
			qp.restore()

			i = i + 1

		i = (-yoffset / self.nodeFieldHeight) - 1
		while (i * self.nodeFieldHeight) <= (-yoffset + geoHeight):
			if i < 0:
				i = i + 1
				continue
			if i >= self.currentNodeCount:
				break

			if i == self.pressedNode:
				qp.setBrush(pressedNodeBrush)

			boundingBox=QRect(0,yoffset+self.timeFieldHeight+self.nodeFieldHeight*i,self.nodeFieldWidth-1,self.nodeFieldHeight)
			qp.drawRect(boundingBox)
			boundingBox=QRect(0,yoffset+self.timeFieldHeight+self.nodeFieldHeight*i+3,self.nodeFieldWidth,self.nodeFieldHeight)
			qp.drawText(boundingBox,Qt.AlignCenter,self._data[i]["name"])

			if i == self.pressedNode:
				qp.setBrush(defaultNodeBrush)

			i = i + 1

		qp.drawRect(0,0,self.nodeFieldWidth,self.timeFieldHeight)


	# def wheelEvent(self,event):
	# 	try:
	# 		self._scroll.wheelEvent(event)
	# 	except Exception, e:
	# 		pass

	def getMouseButton(self,button):
		btn = "4TH"
		if button == Qt.MouseButton.LeftButton:
			btn = "L"
		elif button == Qt.MouseButton.RightButton:
			btn = "R"
		elif button == Qt.MouseButton.MiddleButton:
			btn = "M"
		return btn

	def mousePressEvent(self,event):
		frameAreaGeometry = self.timelineKeyFrameArea.geometry()
		xoffset = frameAreaGeometry.x()
		yoffset = frameAreaGeometry.y()

		pressedNode = (event.y()-self.timeFieldHeight-yoffset)/self.nodeFieldHeight

		btn = self.getMouseButton(event.button())

		if btn == "L" and event.x() < self.nodeFieldWidth and pressedNode >= 0 and len(self._data) > pressedNode:
			self.pressedNode = pressedNode
			self.timelineKeyFrameArea.selectedKeyFrames = []
			self.repaint()

		super(Timeline,self).mousePressEvent(event)

	def mouseMoveEvent(self,event):
		frameAreaGeometry = self.timelineKeyFrameArea.geometry()
		xoffset = frameAreaGeometry.x()
		yoffset = frameAreaGeometry.y()

		movingNode = (event.y()-self.timeFieldHeight-yoffset)/self.nodeFieldHeight

		if self.pressedNode != -1:
			if movingNode < 0:
				movingNode = 0
			if movingNode >= len(self._data):
				movingNode = len(self._data) - 1

			if self.pressedNode != movingNode:
				movingData = self._data.pop(self.pressedNode)
				self._data.insert(movingNode,movingData)

				self._scroll.ensureVisible(-xoffset,movingNode*self.nodeFieldHeight+self.nodeFieldHeight/2,0,self.nodeFieldHeight)


			self.pressedNode = movingNode

			self.update()

		super(Timeline,self).mouseMoveEvent(event)

	def mouseReleaseEvent(self,event):
		frameAreaGeometry = self.timelineKeyFrameArea.geometry()
		xoffset = frameAreaGeometry.x()
		yoffset = frameAreaGeometry.y()

		releaseNode = (event.y()-self.timeFieldHeight-yoffset)/self.nodeFieldHeight
		btn = self.getMouseButton(event.button())

		if btn == "L" and self.pressedNode != -1:
			if releaseNode < 0:
				releaseNode = 0
			if releaseNode >= len(self._data):
				releaseNode = len(self._data) - 1

			self.pressedNode = -1
			self.repaint()
			self.changed.emit()

		super(Timeline,self).mouseReleaseEvent(event)
