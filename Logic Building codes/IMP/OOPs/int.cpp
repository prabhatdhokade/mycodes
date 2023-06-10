#include<bits/stdc++.h>
using namespace std;

class a 
{
    public:
    virtual void fun() =0; 
    void f1(){
        cout<<"a"<<" ";
    }
    virtual void f2(){
        cout<<"a1"<<" ";
    }
    virtual void f3(){
        cout<<"a3"<<" ";
    }
    virtual void f4(){
        cout<<"a4"<<" ";
    }

};
class b:public a 
{
    public:
    void f3(){    
        cout<<"b1"<<" "; 
    }
    void f1(){  
        cout<<"b2"<<" ";
    }
    void f5(int a){   // method overriding
        cout<<"b222"<<" ";
    }
    void fun(){
        cout<<"b.fun"<<" "; 
    }
   
};

template<class x>   // function template or generic function 
x big(x a , x b){
    if(a > b) return a;
    else return b;
}

int main(){
  b o2;
  a *p;
  p = &o2;
  p->f1();     // parent class a's function f2 will get called before virtual fun(early binding)
  p->f2();
  p->f3();
  p->f4();
  p->fun();
  cout<<big(2,3)<<" ";
  cout<<big(3.5,5.5)<<" ";
}