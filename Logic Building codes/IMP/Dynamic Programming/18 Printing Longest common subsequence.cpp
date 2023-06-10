/* Printing Longest Common Subsequence
Given two sequences, print the longest subsequence present in both of them.
Example:
LCS for input Sequences “ABCDGH” and “AEDFHR” is “ADH” of length 3. */

#include<bits/stdc++.h>
using namespace std;

string lcs(string s1,string s2,int n,int m) {
    int t[n+1][m+1];

    for(int i=0;i<n+1;i++){     // thsi is same as length of lcs problem
        for(int j=0;j<m+1;j++) {
            if( i == 0 || j==0) {
                t[i][j] =0;
            }
        }
    }

    for(int i=1;i<n+1;i++){
        for(int j=1;j<m+1;j++) {
            if( s1[i-1] == s2[j-1]) {
                t[i][j] = 1 + t[i-1][j-1];
            }
            else 
                t[i][j] = max(t[i-1][j] , t[i][j-1]);
        }
    } 

    string s =" ";

    int i =n;
    int j =m;

    while( i>0 && j>0) {
        
        if( s1[i-1] == s2[j-1] ) {    // we'll start from t[n][m] of the matrix,if the last index of both string is equal we'll 
            s.push_back(s1[i-1]); // move towards the last index we came from
            i--;  // this is a bit f-step u have to give attension to it try it on papaer plz
            j--; // or watch the video again
        }
        else // if we didn't  found similar we'll move towards max of the nearer 
            if(t[i][j-1] > t[i-1][j]) { // just try to implement matrix on paper
                j--;
            }
            else 
                i--;
    }       
    reverse(s.begin(),s.end()); // we get the string in reverse so we have to do shot
    return s;
}

int main() {
    string s1;
    cin>>s1;
    string s2;
    cin>>s2;
    int n,m;
    n = s1.size();
    m = s2.size();

    cout<<lcs(s1,s2,n,m);
}