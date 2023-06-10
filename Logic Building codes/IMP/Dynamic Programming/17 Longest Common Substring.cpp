/* Longest Common Substring(Dynamic Programming)
Given two strings ‘X’ and ‘Y’, find the length of the longest common substring.
Examples:

Input : X = “GeeksforGeeks”, y = “GeeksQuiz”
Output : 5
The longest common substring is “Geeks” and is of length 5.
*/


#include<bits/stdc++.h>

using namespace std;

int lcs(string x,string y,int n,int m) {
    int t[n+1][m+1];
    
    for(int i =0;i<n+1;i++){
        for(int j=0;j<m+1;j++){
            if(i==0 || j==0) {
                t[i][j] = 0;
            }
        }
    }

    for(int i =1;i<n+1;i++){
        for(int j=1;j<m+1;j++){
            if(x[i-1] == y[j-1]) {    // chek if it is equal or not
                t[i][j] = 1 + t[i-1][j-1];
            }
            else 
                t[i][j] = 0;  // if it discontinues then we'll make the count zero 
                            // then we will start from zero again
        }
    }

    /* here we have to do something extraa work 
    I missed , is that at last we have to return the max value in the matrix and 
    not t[m][n]. Just traverse through the matrix once and store max value in a 
    variable and return that. Why it is so? Cuz substring can exist anywhere in between. 
    Just think a bit about it bit and you will understand. */
    int ans =0;
    for(int i =1;i<n+1;i++) {
        for(int j=0;j<m+1;j++){
            ans = max(ans,t[i][j]);
        }
    }
    return ans;
}

int main() 
{
    string x;
    cin>>x;
    string y;
    cin>>y;
    int n;
    n=x.length();
    int m;
    m=y.length();
    cout<<lcs(x,y,n,m);
}