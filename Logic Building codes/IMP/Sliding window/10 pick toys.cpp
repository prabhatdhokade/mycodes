/* John is at a toy store help him pick maximum number of toys. He can only select in a continuous manner and he can select only two types of toys.


Example:
Input: abaccab 
op : 4
*/

#include<bits/stdc++.h>

using namespace std;

int solve(int n,string s){
    unordered_map<char,int> m;
    int i=0,j=0,ans=0;
    while(j<n){
        m[s[j]]++;

        if(m.size() < 2) j++;
        else if( m.size() == 2){
            ans = max(ans,j-i+1);
            j++;
        }
        else if(m.size() > 2){
            while(m.size() > 2){
                m[s[i]]--;
                if(m[s[i]] == 0){
                    m.erase(s[i]);
                }
                i++;
            }
            j++;
        }
    }
    return ans;
}

int main() {
    string s;
    cin>>s;
    int n = s.length();
    cout<<solve(n,s);
}