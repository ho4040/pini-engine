#ifndef __BSP_NODE_H__
#define __BSP_NODE_H__

#include "BSPImage.h"

// Node
class BSPNode
{
public:
	int x;
	int y;
	int width;
	int height;

private:
	BSPNode* children[2];

	BSPImage *image;
public:

	BSPNode(int x, int y, int width, int height);
	~BSPNode();

	BSPNode *left() { return children[0];}
	BSPNode *right() { return children[1];}

	void verticalSplit(int w1, int w2);
	void horizontalSplit(int h1, int h2);

	bool containable(int width, int height);

	void assign(BSPImage *image);

	bool assigned();

	// debug
	void printImageInfo();
};

#endif