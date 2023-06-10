/* Given a string you need to print the size of the longest possible substring that has exactly k unique characters.


Example:
Input:
aabacbebebe
3
Output:
7
*/
// input : 11
//:aabacbebebe
//: 3
 // output : 7

#include<bits/stdc++.h>

using namespace std;

/*int main() 
{
 
 string s;
 cin>>s;
 int k;
 cin>> k;

 int i,j;
 i=j=0;
 int ans = 0;

 unordered_map<char,int> mpp;

 while( j< s.size()) 
    {
        mpp[s[j]]++;

        if( mpp.size() < k) {
            j++;
        }

        else if ( mpp.size() == k) {
            ans = max( ans, j-i+1);
            j++;
        }

        else if ( mpp.size() > k) {
            while ( mpp.size() > k) {   // we have to loop it util map.size < k
                mpp[s[i]]--;    
                if ( mpp[s[i]] == 0) { // if the count of mpp.s[i] hits zero we have
                    mpp.erase(s[i]);   // to remove it from map
                }
                i++;   
            }
            j++;
        }

    }
    cout << ans;

} */

int solve(int n,string s,int k){
    unordered_map<char,int> m;
    int i=0,j=0,ans=-1;
    while(j<n){
        m[s[j]]++;

        if(m.size() < k){
            j++;
        }
        else if(m.size() == k){
            ans = max(ans,j-i+1);
            j++;
        }
        else if(m.size() > k){
            while(m.size() > k){
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
    int k;
    cin>>k;
    cout<<solve(n,s,k);
}
