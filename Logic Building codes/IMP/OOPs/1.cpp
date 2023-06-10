#include<bits/stdc++.h>
using namespace std;

class student{
    string name;
    public:
    int age;
    int gender;

    student(){
        cout<< " default constructor"<<" ";
    }  // default constructor
  
    student(string s,int i,int m){
        name =s;
        age = i;
        gender = m;
    }   // parameterised constructor

    void setname(string s){
        name = s;
    }
    void getname(){
        cout<< name<<" ";
    }
    void print(){
        cout<<name<<" ";
        cout<<age<<" ";
        cout<<gender<<"\n";
    }
    ~student(){
        cout<< " delete";
    }
};

int main() {
    
/*
    student arr[3];
    string s;
    for(int i=0;i<3;i++){
    cin>>s;
    arr[i].setname(s);
    cin>>arr[i].age;
    cin>>arr[i].gender;
    }
    for(int i=0;i<3;i++){
    arr[i].getname();
    arr[i].print();
 
    }
*/

    student a("prabhu",21,1);

    student b = a;
    b.print();
}