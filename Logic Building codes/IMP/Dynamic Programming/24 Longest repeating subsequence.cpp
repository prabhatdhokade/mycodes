/* Longest Repeating Subsequence
Given a string, print the longest repeating subsequence such that the two subsequence don’t have same string character at same position, i.e., any i’th character in the two subsequences shouldn’t have the same index in the original string.
Example:
Input: str = "aab"
Output: "a"
The two subsequence are 'a'(first) and 'a' 
(second). Note that 'b' cannot be considered 
as part of subsequence as it would be at same
index in both.*/

#include<bits/stdc++.h>

using namespace std;

int lcs(string s1,int n){
    string s2 = s1;
    int m=n;

    int t[n+1][m+1];
    for(int i=0;i<n+1;i++){
        for(int j=0;j<m+1;j++){
            if(i==0 ||j==0) {
                t[i][j] =0;
            }
        }
    }
    for(int i =1;i<n+1;i++) {
        for(int j=1;j<m+1;j++){
            if(s1[i-1] == s2[j-1] && i!=j) { // this is imp,we want the same repeating lcs,so it should not match with the previous lcs's indexex so we have writeen i!=j
                t[i][j] = 1 + t[i-1][j-1]; 
            }
            else 
                t[i][j] = max ( t[i][j-1] , t[i-1][j] );
        }
    }

    return t[n][m];
}


int main()
{
    string s1;
    cin>>s1;
    int n;
    n=s1.length();
    cout<<lcs(s1,n);
}