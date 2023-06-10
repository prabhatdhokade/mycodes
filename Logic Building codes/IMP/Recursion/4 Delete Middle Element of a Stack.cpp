#include<bits/stdc++.h>
using namespace std;
//not correct code plz try again
void solve(stack<int>&s, int k) {
    if(k == 1){
        s.pop();
        return;
    }
    int temp = s.top();
    solve(s,k-1);
    s.push(temp);
    return;
}


stack<int>midele(stack<int>s,int n) {
    if(s.size() == 0){
        return s;
    }
    int k = n/2 + 1;
    solve(s,k);
    for(int i =0; i< s.size() ; i++) {
        cout<<s.top()<<" ";
        s.pop();
    }
    return s;
}


int main() 

{
    int n;
    cin >> n;
    int a;

    stack<int> s;
    for(int i =0; i<n  ; i++) {
        cin>>a;
        s.push(a);
    }
    
    midele(s,s.size());

    

}