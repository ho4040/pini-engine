#include "BSPNode.h"
#include <iostream>

BSPNode::BSPNode(int x, int y, int width, int height)
{
	this->x = x;
	this->y = y;
	this->width = width;
	this->height = height;

	children[0] = NULL;
	children[1] = NULL;

	image = NULL;
}
BSPNode::~BSPNode()
{
	if(children[0])
	{
		delete children[0];
		children[0] = NULL;
	}
	if(children[1])
	{
		delete children[1];
		children[1] = NULL;
	}

	delete image;
}
void BSPNode::verticalSplit(int w1, int w2)
{
	BSPNode *node1 = new BSPNode(x,    y, w1, height);
	BSPNode *node2 = new BSPNode(x+w1, y, w2, height);

	children[0] = node1;
	children[1] = node2;
}
void BSPNode::horizontalSplit(int h1, int h2)
{
	BSPNode *node1 = new BSPNode(x, y,    width, h1);
	BSPNode *node2 = new BSPNode(x, y+h1, width, h2);

	children[0] = node1;
	children[1] = node2;
}

void BSPNode::assign(BSPImage *image)
{
	this->image = image;
}

bool BSPNode::containable(int width, int height)
{
	return width <= this->width && height <= this->height;
}

bool BSPNode::assigned()
{
	return image != NULL;
}

// debug
void BSPNode::printImageInfo()
{
	if(image)
	{
		std::cout << "(" << (image->x+x) << " " << (image->y+y)
			<< " " << (image->width+x) << " " << (image->height+y) << " )" << std::endl;
	}
}