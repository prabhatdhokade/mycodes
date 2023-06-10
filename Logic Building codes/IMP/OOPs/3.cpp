#include<iostream>
using namespace std;

class A{
    int i,j;

    public:
       void add()
        {
            cout<<"This is in A"<<endl;
        }
};

class B:public A{
    int i=2,j=3;

    public:
        void add()
        {
            cout<<"This is in B"<<endl;
        }
};

class C:public A{


    public:
        void add()
        {
            cout<<"This is in C"<<endl;
        }
};

class D:public B,public C{
    int i=2,j=3;

    public:
        void add()
        {
            cout<<"This is in D"<<endl;
        }
};



int main()
{
    D a;

    a.C::add();

}



