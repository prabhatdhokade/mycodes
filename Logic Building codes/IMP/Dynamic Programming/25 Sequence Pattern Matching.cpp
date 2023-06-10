/* Given two strings s and t, return true if s is a subsequence of t, or false otherwise.

A subsequence of a string is a new string that is formed from the original string by 
deleting some (can be none) of the characters without disturbing the relative positions 
of the remaining characters. (i.e., "ace" is a subsequence of "abcde" while "aec" is not).


*/

#include<bits/stdc++.h>

using namespace std;

bool lcs(string s1,string s2,int n,int m) {
    int t[n+1][m+1];
    for(int i=0;i<n+1;i++) {
        for(int j=0;j<m+1;j++) {
            if(i==0 || j==0) {
                t[i][j] =0;
            }
        }
    }

    for(int i=1;i<n+1;i++){
        for(int j=1;j<m+1;j++) {
            if(s1[i-1] == s2[j-1]) {
                t[i][j] = 1+t[i-1][j-1];
            }
            else 
                t[i][j] = max(t[i-1][j] , t[i][j-1]);
        }
    }

    int ans = t[n][m];

    if(ans == n ) {
        return true;
    }
    else 
        return false;
}


int main() {

    string s1;
    cin>>s1;
    string s2;
    cin>>s2;
    int n,m;
    n=s1.length();
    m=s2.length();
    cout<< lcs(s1,s2,n,m);

}