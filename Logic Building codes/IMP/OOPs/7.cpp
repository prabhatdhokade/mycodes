#include<bits/stdc++.h>


using namespace std;

int main(){
    string s1;
    string s2;
    cin>>s1>>s2;

    unordered_map<int,char> m;
    for(int i=0;i<s1.size();i++){
        m[s1[i]]++;
    }
    for(int i=0;i<s2.size();i++){
        m[s2[i]]++;
    }
    vector<int>v;
    cout<<m.size();
}