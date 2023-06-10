#include<bits/stdc++.h>

using namespace std;
void swap(stack<int>&s,int ele) 
{
    if(s.size() == 0){
        s.push(ele);
    }
    int temp = s.top();
    s.pop();
    swap(s,ele);
    s.push(temp);
    return;
}

void reverse(stack<int>&s) {
    if(s.size() == 1){
        return;
    }
    int val = s.top();
    s.pop();
    reverse(s);
    swap(s,val);
    return;

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
    reverse(s);

    for(int i =0; i < n; i++) {
        int n = s.top();
        cout<<n<<" ";
        s.pop();
    }
}