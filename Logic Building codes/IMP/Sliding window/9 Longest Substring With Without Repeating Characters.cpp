/*Given a string s, find the length of the longest substring without repeating characters.

 

Example 1:

Input: s = "abcabcbb"
Output: 3
Explanation: The answer is "abc", with the length of 3. */


// input : 6
//         pwwkew
// output : 3 

#include<bits/stdc++.h>

using namespace std;
/*
int main() 
{
 
 string s;
 cin>>s;
 

 int i,j;
 i=j=0;
 int ans = 0;

 unordered_map<char,int> mpp;

 while( j< s.size()) 
    {
        mpp[s[j]]++;

       // if( mpp.size() < j-i+1 ) {  This condtion will never hit 
         //   j++;
        //}                              

        if ( mpp.size() == j-i+1) {
            ans = max( ans, j-i+1);
            j++;
        }

        else if ( mpp.size() < j-i+1) {
            while ( mpp.size() < j-i+1) {   // we have to loop it util map.size < k
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
}
*/

int solve(int n,string s){
    int i=0,j=0,ans=-1;
    unordered_map<char,int> m;
    while(j<n){
       m[s[j]]++;
        if(m.size() == j-i+1){
            ans = max(ans,j-i+1);
            j++;
        }
        else if(m.size() < j-i+1){
            while(m.size() < j-i+1){
                m[s[i]]--;
                if(m[s[i]] == 0){   // this step is little wanky got stuck it here
                    m.erase(s[i]);
                }
                i++;
            }
            j++;
        }
    }
    return ans;
}

int main()
{
    string s;
    cin>>s;
    int n;
    n =s.length();
    cout<<solve(n,s);
}



