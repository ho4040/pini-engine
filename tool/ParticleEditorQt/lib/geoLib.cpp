#include "geoLib.h"
#include <math.h>


Vector2d::Vector2d()
{
    x=0;y=0;
}

Vector2d::Vector2d(float x,float y)
{
    this->x=x;
    this->y=y;
}

Vector2d::~Vector2d()
{

}

Vector2d Vector2d::operator+(Vector2d v)
{
    return Vector2d(this->x+v.x,this->y+v.y);
}

Vector2d Vector2d::operator-(Vector2d v)
{
    return Vector2d(this->x-v.x,this->y-v.y);
}

Vector2d Vector2d::operator*(float a)
{
    return Vector2d(this->x*a,this->y*a);
}

Vector2d Vector2d::operator/(float a)
{
    return Vector2d(this->x/a,this->y/a);
}

Vector2d Vector2d::operator+=(Vector2d v)
{
    return Vector2d(this->x+=v.x,this->y+=v.y);
}

Vector2d Vector2d::operator-=(Vector2d v)
{
    return Vector2d(this->x-=v.x,this->y-=v.y);
}

Vector2d Vector2d::operator*=(float a)
{
    return Vector2d(this->x*=a,this->y*=a);
}

Vector2d Vector2d::operator/=(float a)
{
    return Vector2d(this->x/=a,this->y/=a);
}

Vector2d Vector2d::operator=(Vector2d v)
{
    return Vector2d(this->x=v.x,this->y=v.y);
}

float Vector2d::len()
{
    return sqrtf(x*x +y*y);
}

Vector2d Vector2d::normalize()
{
    return Vector2d(x/this->len(),y/this->len());
}




Color3d::Color3d()
{

}

Color3d::Color3d(int r,int g,int b)
{
    this->red=r;
    this->green=g;
    this->blue=b;
//    if (r<0)
//        this->red=0;
//    if(r>255)
//        this->red=255;
//    if (g<0)
//        this->green=0;
//    if(g>255)
//        this->green=255;
//    if (b<0)
//        this->blue=0;
//    if(b>255)
//        this->blue=255;

}

Color3d::~Color3d()
{

}



Color3d Color3d::operator+(Color3d v)
{
    return Color3d(this->red+v.red,this->green+v.green,this->blue+v.blue);
}

Color3d Color3d::operator-(Color3d v)
{
    return Color3d(this->red-v.red,this->green-v.green,this->blue-v.blue);
}

Color3d Color3d::operator*(float v)
{
    return Color3d(this->red*v,this->green*v,this->blue*v);
}

Color3d Color3d::operator/(float v)
{
    return Color3d(this->red/v,this->green/v,this->blue/v);
}

Color3d Color3d::operator+=(Color3d v)
{
    return Color3d(this->red+=v.red,this->green+=v.green,this->blue+=v.blue);
}

Color3d Color3d::operator-=(Color3d v)
{
    return Color3d(this->red-=v.red,this->green-=v.green,this->blue-=v.blue);
}

Color3d Color3d::operator*=(float v)
{
    return Color3d(this->red*=v,this->green*=v,this->blue*=v);
}

Color3d Color3d::operator/=(float v)
{
    return Color3d(this->red/=v,this->green/=v,this->blue/=v);
}

Color3d Color3d::operator=(Color3d v)
{
    return Color3d(this->red=v.red,this->green=v.green,this->blue=v.blue);
}

float Color3d::len()
{
    return sqrtf(red*red + green*green + blue*blue);
}

//float dot(Vector2d v); //내적 = A*b*cOS(
//float cross(Vector2d v); //외적 a*b*sIN(
Color3d Color3d::normalize()
{
    return Color3d(red/this->len(),green/this->len(),blue/this->len());
}
