#include<bits/stdc++.h>

using namespace std;

int  solve(string s1,string s2) {
    unordered_map<char ,int > m;
    for(int i=0;i<s2.length();i++) {
        m[s2[i]]++;
    }

    int count = m.size();

    int i=0;
    int j=0;
    int ans =0;
    int n = s1.length();
    int k = s2.length();

    while(j<n) {
        
        if(m.find(s1[j]) != m.end()) {
            m[s1[j]]--;
            if( m[s1[j]] == 0) count--;
        }

        if( j-i+1 < k) {
            j++;
        }

        else if( j-i+1 == k) {

            if ( count == 0) {
                ans++;
            }
            if(m.find(s1[i]) != m.end()) {
                m[s1[i]]++;
                if(m[s1[i]] >0 ) count++;
            }
            i++;
            j++;
        }
    }

    return ans;
}

int main()
{
    string s1;
    cin>>s1;
    string s2;
    cin>>s2;
    cout<<solve(s1,s2);
}