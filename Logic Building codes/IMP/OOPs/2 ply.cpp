#include<bits/stdc++.h>
using namespace std;

class complex{
    private:
        int in,rn;
    public:
    complex(){

    }
    complex(int i, int r){
        in = i;
        rn =r;
    }
    complex operator + (complex const &obj){
        complex res;
        res.in = in + obj.in;
        res.rn = rn + obj.rn;
        return res;
    }   

    void print(){
        cout<< in<<" ";
        cout<<rn;
    }
};

int main(){

    complex c1(10,2);
    
}