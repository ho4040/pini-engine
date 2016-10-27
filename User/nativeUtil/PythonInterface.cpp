#include "BSPAlgoritm.h"
#include "BSPNode.h"
#include "BSPImage.h"


//////////////////////////////////
//// BSP INTERFACE
extern "C"{
	BSPNode* _bsp_root = nullptr;
	void BSP_new(int w,int h){
		_bsp_root = new BSPNode(0,0,w,h);
	}

	void BSP_delete(){
		delete _bsp_root;
	}

	void BSP_add(char* id, int w,int h){
		BSPAlgorithm::insert(_bsp_root,new BSPImage(id,0,0,w,h));
	}

	char* BSP_json(){
		return (char*)BSPAlgorithm::toJsonString(_bsp_root).c_str();
	}
}