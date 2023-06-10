/*  Given n pairs of parentheses, write a function to generate all 
combinations of well-formed parentheses of length 2*n.

For example, given n = 3, a solution set is:

"((()))", "(()())", "(())()", "()(())", "()()()"


Very very important Question
*/

#include<bits/stdc++.h> 
using namespace std;

void solve(int open, int close,string op,vector<string>&v) {
    if(open == 0 && close == 0) {
        v.push_back(op);
        return;
    }
    if(open!=0) {

        string op1 = op;
        op1.push_back('(');
        solve(open-1,close,op1,v);
    }
    if(close>open) {
        string op2 = op;
        op2.push_back(')');
        solve(open,close-1,op2,v);
    }
}

void ans(int n) {
    vector<string>v;
    int open = n;
    int close = n;
    string op ="";
    solve(open,close,op,v);
    for(auto it=v.begin(); it!= v.end(); it++) {
        cout<< *it<<",";
    }
}


int main() 
{
    int n;
    cin>>n;

    ans(n);
    
}