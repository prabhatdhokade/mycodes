/*Given two strings X and Y, print the shortest string that has both X and Y as
subsequences. If multiple shortest supersequence exists, print any one of them.

Examples:

Input: X = "AGGTAB",  Y = "GXTXAYB"
Output: "AGXGTXAYB" OR "AGGXTXAYB" 
OR Any string that represents shortest
supersequence of X and Y

Input: X = "HELLO",  Y = "GEEK"
Output: "GEHEKLLO" OR "GHEEKLLO"
OR Any string that represents shortest 
supersequence of X and Y */

#include<bits/stdc++.h>

using namespace std;

string lcs(string s1,string s2,int n,int m ){
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

    int i = n;
    int j = m;
    string s ="";

    while(i>0 && j>0) {
        if(s1[i-1] == s2[j-1]) {
            s.push_back (s1[i-1]);
            i--;
            j--;
        }
        else 
            if(t[i-1][j] > t[i][j-1] ) {
                s.push_back(s1[i-1]);
                i--;
            }
            else {
                s.push_back(s2[j-1]);
                j--;
            }
    }

    while(i>0) {      // this is important step,in upper while loop if we hit the 0 first then our string wont print whole string
        s.push_back(s1[i-1]); // so if there is something reamining string,then this loop will print it 
        i--;
    }
    while(j>0) {
        s.push_back(s2[j-1]);
        j--;
    }
    reverse(s.begin(),s.end());
    return s;

 }


int main() {
    string s1;
    cin>>s1;
    string s2;
    cin>>s2;
    int n,m;
    n = s1.length();
    m =s2.length();
    cout<< lcs(s1,s2,n,m);
}