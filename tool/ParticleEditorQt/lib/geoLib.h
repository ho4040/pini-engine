#ifndef GEOLIB_H
#define GEOLIB_H

class Vector2d //2차원 Vector 클래스 참고 // 벡터끼리 사칙연산 되도록 연산자 오버라이딩
{
public:
    float x;
    float y;

//dot=>숫자, cross=>벡터
//normalize 벡터정규화
//length
    Vector2d();
    Vector2d(float x,float y);
    ~Vector2d();


    float len();
    //float dot(Vector2d v); //내적 = A*b*cOS(
    //float cross(Vector2d v); //외적 a*b*sIN(
    Vector2d normalize();


    Vector2d operator+(Vector2d v);
    Vector2d operator-(Vector2d v);
    Vector2d operator*(float v);
    Vector2d operator/(float v);
    Vector2d operator+=(Vector2d v);
    Vector2d operator-=(Vector2d v);
    Vector2d operator*=(float v);
    Vector2d operator/=(float v);
    Vector2d operator=(Vector2d v);
};

class Matrix2d //Cocos2d-x, vector2d랑 곱하기 연산 할 수 있도록 연산자 오버라이딩.
{
    float a,b,c,d;
};

class Color3d
{
public:
    float red;
    float green;
    float blue;

    Color3d();
    Color3d(int r,int g,int b);
    ~Color3d();

    float len();
    //float dot(Vector2d v); //내적 = A*b*cOS(
    //float cross(Vector2d v); //외적 a*b*sIN(
    Color3d normalize();


    Color3d operator+(Color3d v);
    Color3d operator-(Color3d v);
    Color3d operator*(float v);
    Color3d operator/(float v);
    Color3d operator+=(Color3d v);
    Color3d operator-=(Color3d v);
    Color3d operator*=(float v);
    Color3d operator/=(float v);
    Color3d operator=(Color3d v);

};


/*
class Line
{
};
class LineSegment
{
};
class polygon
{
};
class convex
{
};
*/

#endif // GEOLIB_H
