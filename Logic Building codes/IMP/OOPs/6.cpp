#include<bits/stdc++.h>

using namespace std;

int main(){
    int n;
    cin>>n;
    vector<int> v;
.
    while(n>0){
        int a =0;
        a = n % 10;
        if(a == 0) a += 1;
        else if(a % 2 == 0){
            a = a +1;
        }
        else if(a % 2 !=0 ){
            a -= 1;
        }
        v.push_back(a);
        n = n / 10;
    }
    reverse(v.begin(),v.end());
    for(int i=0;i<v.size();i++){
        cout<<v[i];
    }
}