#ifndef __BSP_ALGORITM_H__
#define __BSP_ALGORITM_H__

#include "BSPNode.h"
#include <string>

class BSPAlgorithm
{
public:
	static BSPNode* insert(BSPNode *root, BSPImage *image);

	static BSPNode *findContainableNode(BSPNode *node, int width, int height);

	static void print(BSPNode *node);

	static std::string toJsonString(BSPNode *node);
};

#endif