/* Shortest Common Supersequence
Given two strings str1 and str2, find the shortest string that has both str1 and str2 as subsequences.
Examples:

Input:   str1 = "geek",  str2 = "eke"
Output: "geeke"  

PROBLEM STATEMENT LINK https://www.geeksforgeeks.org/shortest-common-supersequence/*/

#include<bits/stdc++.h>

using namespace std;

int lcs(string s1,string s2,int n,int m ){
    int t[n+1][m+1];
    for(int i =0;i<n+1;i++) {
        for(int j=0;j<m+1;j++) {
            if(i==0 || j==0) {
                t[i][j] = 0;
            }
        }
    }
    for(int i=1;i<n+1;i++) {
        for(int j=1; j<m+1;j++) {
            if(s1[i-1] == s2[j-1]) {
                t[i][j] = 1+ t[i-1][j-1];
            }
            else 
                t[i][j] = max(t[i-1][j] , t[i][j-1]);
        }
    }

    return t[n][m];
}

int solve(string s1,string s2,int n,int m) {
    int ans =0;
    ans = n+ m - lcs(s1,s2,n,m);  // we subtract the LCS from their sums 
    return ans;// we get the shortest supersequence
}

int main() {
    string s1;
    cin>>s1;
    string s2;
    cin>>s2;
    int n,m;
    n = s1.length();
    m =s2.length();
    cout<< solve(s1,s2,n,m);
}