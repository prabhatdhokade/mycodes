#include<bits/stdc++.h>
// not running well
using namespace std;
int  push(int a);
int pop(int a);
int getmin();
stack<int> s;
stack<int> ss;
int main() 
{
    int n;
    cin>>n;
    for ( int i =0; i<n ; i++) {
        push(i);
    }
    //s.pop(15);
    cout<<getmin();
}

    int push(int a) {
        s.push(a);
        if ((ss.size() == 0 ) || ss.top() >= a ) { 
            ss.push(a);
        }
    return 0;
    }

    int getmin() {
        if ( ss.size() == 0 ) {
            return -1;
        }
        return ss.top();
    }
    int pop() {
        if(s.size() == 0 ) {
            return -1;
        }
        int ans = s.top();
            s.pop();
        if(ss.top() == ans) {
            ss.pop();
        }
    }
