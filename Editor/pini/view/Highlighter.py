# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide.QtGui import * 
from PySide.QtCore import *
import re

class Highlighter(QSyntaxHighlighter):
	# 문법강조 규칙
	def __init__(self, parent=None):
		super(Highlighter, self).__init__(parent)
		self.rules = []

		cmdsFormat = QTextCharFormat()
		cmdsFormat.setForeground(QColor(152,226,45))
		self.rules.append(([0],r"(?<!\[)\[[^\[].*? (?=.*\])",cmdsFormat))
		self.rules.append(([0],r"(?<!\[)\[[^\[][^ ]*?\]",cmdsFormat))
		self.rules.append(([1],r"(\])|(\[\[.*?\])|([,;][^\[]*\])|(\".*?\")",cmdsFormat))

		gotoFormat = QTextCharFormat()
		gotoFormat.setFontWeight(QFont.Bold);
		gotoFormat.setForeground(QColor(166,220,38))
		self.rules.append(([0],r"^\t*\>[^\n\s]+",gotoFormat))

		markFormat = QTextCharFormat()
		markFormat.setForeground(QColor(98,215,229))
		self.rules.append(([0],r"(?<=[^\<])\<[^\<].*?\>",markFormat))

		numFormat = QTextCharFormat()
		numFormat.setForeground(QColor(167,114,241))
		self.rules.append(([0],r'(?<!\t)(?<=\=|\s)\d+',numFormat))
		self.rules.append(([0],ur'(?<![a-zA-z_가-힣ㄱ-ㅎㅏ-ㅣ])\-?[0-9]+\.[0-9]+',numFormat))
		self.rules.append(([1],ur'((?<![a-zA-Z_가-힣ㄱ-ㅎㅏ-ㅣ.])(참|거짓)(?![a-zA-Z_가-힣ㄱ-ㅎㅏ-ㅣ.]))|(^\t*[;,].*)',numFormat))

		funFormat = QTextCharFormat()
		funFormat.setForeground(QColor(245,9,97))
		funFormat.setFontWeight(QFont.Bold);
		self.rules.append(([0],ur"^\t*\@[a-zA-Z_가-힣ㄱ-ㅎㅏ-ㅣ][a-zA-Z_0-9가-힣ㄱ-ㅎㅏ-ㅣ.]*",funFormat))
		self.rules.append(([0],r"=",funFormat))

		quoFormat = QTextCharFormat()
		quoFormat.setForeground(QColor(228,219,109))
		self.rules.append(([0],r'".*?"',quoFormat))

		commentFormat = QTextCharFormat()
		commentFormat.setForeground(QColor(117,113,94))
		self.rules.append(([1],r'(\#.*)|(".*?")|(^\t*[;,].*)',commentFormat))

		ATLLineFormat = QTextCharFormat()
		ATLLineFormat.setForeground(QColor(245,9,97))
		self.rules.append(([0],r"\t+\&",ATLLineFormat))

		semiFormat = QTextCharFormat()
		semiFormat.setForeground(QColor(255,128,0))
		self.rules.append(([0],r"^\t*[;,]",semiFormat))

		'''
		xlxsFormat = QTextCharFormat()
		xlxsFormat.setForeground(QColor(170,119,119))
		self.rules.append((u(r'\?\'.*?\.xlsx\'.*?\?'),xlxsFormat))
		'''

	def highlightBlock(self, text):
		for group, pattern, format in self.rules:
			for m in re.finditer(pattern, text):
				if m:
					isFound = False

					for i in range(0,len(group)):
						r = m.group(group[i])

						if r != None:
							isFound = True
							break

					if isFound:
						index = m.start()
						length= m.end()-m.start()
						self.setFormat(index, length, format)

		self.setCurrentBlockState(0)
		'''
		startIndex = 0
		if self.previousBlockState() != 1:
			startIndex = self.commentStartExpression.indexIn(text)

		while startIndex >= 0:
			endIndex = self.commentEndExpression.indexIn(text, startIndex)

			if endIndex == -1:
				self.setCurrentBlockState(1)
				commentLength = len(text) - startIndex
			else:
				commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

			self.setFormat(startIndex, commentLength, self.multiLineCommentFormat)
			startIndex = self.commentStartExpression.indexIn(text, startIndex + commentLength);
		'''
