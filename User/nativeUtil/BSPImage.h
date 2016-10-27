#ifndef __BSP_IMAGE_H__
#define __BSP_IMAGE_H__

#include <string>

// Image
// rect 영역을 지정한다
class BSPImage
{
public:
	int x,y,width,height;

	std::string id;

	BSPImage(){}
	BSPImage(char* _id,int x, int y, int width, int height)
	{
		id = std::string(_id);

		this->x = x;
		this->y = y;
		this->width = width;
		this->height = height;
	}
};

#endif