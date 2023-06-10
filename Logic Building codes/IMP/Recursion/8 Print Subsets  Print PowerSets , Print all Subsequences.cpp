// input : abc
// output : c b bc a ac ab abc , plz chek out the video again this imp question   

#include<bits/stdc++.h>

using namespace std;
void solve(string ip,string op) {
    if(ip.length()==0){
        cout<<op<<" ";
        return;
    }
    string op1=op;    // set the values to output string
    string op2=op;    // same as 
    op2.push_back(ip[0]);  // push the first element into the other output
    ip.erase(ip.begin() + 0); //erase the 0th index of the string 
    solve(ip,op1);     //pass the values it recursion will do its work
    
    solve(ip,op2);
}
int main() 
{
    string s1;
    cin >> s1;
    string s2 =""; // for output purpose
    solve(s1,s2);
}

