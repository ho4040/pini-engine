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
