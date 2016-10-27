#include "BSPAlgoritm.h"
#include <iostream>

BSPNode * BSPAlgorithm::insert(BSPNode *root, BSPImage *image)
{
	while(1)
	{
		BSPNode *container = findContainableNode(root, image->width, image->height);

		if(container == NULL)
		{
			// full
			return NULL;
		}

		if(image->width == container->width &&
			image->height == container->height)// fit
		{
			container->assign(image);
			return container;
		}
		else
		{
			int extraSpace1 = container->width * (container->height - image->height);
			int extraSpace2 = container->height * (container->width - image->width);

			if(extraSpace1 > extraSpace2)
				container->horizontalSplit(image->height, container->height - image->height);
			else
				container->verticalSplit(image->width, container->width - image->width);
		}
	}
}

BSPNode *BSPAlgorithm::findContainableNode(BSPNode *node, int width, int height)
{
	if(node == NULL || node->assigned())
		return NULL;


	if(node->left() && node->right())
	{
		BSPNode *output = NULL;

		output = findContainableNode(node->left(), width, height);
		BSPNode *rightN = findContainableNode(node->right(), width, height);

		if(!output) output = rightN;
		return output;
	}
	else if(node->containable(width, height))
	{
		return node;
	}

	return NULL;
}

void BSPAlgorithm::print(BSPNode *node)
{
	if(!node)
		return;
	if(node->assigned())
	{
		node->printImageInfo();
		return;
	}
	if(node->left())
		print(node->left());
	if(node->right())
		print(node->right());
}

std::string BSPAlgorithm::toJsonString(BSPNode *node){
	return "";
}
