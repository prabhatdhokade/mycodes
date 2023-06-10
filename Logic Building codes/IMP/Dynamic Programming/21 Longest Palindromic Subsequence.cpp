#include<bits/stdc++.h>

using namespace std;

int lcs(string s1,string s2,int n,int m) {
    int t[n+1][m+1];

    for(int i=0 ;i<n+1;i++) {
        for(int j=0;j<m+1;j++) {
            if(i==0 || j ==0) {
                t[i][j] = 0;
            }
        }
    }

   for(int i =1;i<n+1;i++){
        for(int j=1;j<m+1;j++){
            if(s1[i-1] == s2[j-1]) {
                t[i][j] = 1 + t[i-1][j-1];
            }
            else 
                t[i][j] = max(t[i-1][j] , t[i][j-1]);
        }
    }
    
    return t[n][m];
    
    }


int lps(string s1,int n) {
    string s2;
    string s3 = s1;  // save s1 into a s3 beacuse we are going to reverse it an then when we call lcs we get the exact same,so we get the wrong ans,that thing fucked a whole night plz chek it once
    reverse(s1.begin() , s1.end());  // this is iportant step we reverse the string and the put it in s2, just think abut why would we reverse
    s2 =s1;
    //cout<<s2<<" ";
    int m =n;
    int ans =0;
    ans = lcs(s3,s2,n,m); // so we can lcs,just think once more and watch the video
    return ans;
}                                   

int main() {
    string s1;
    cin>>s1;
    int n = s1.size();
    cout<<lps(s1,n);  // lps = longest Palindrome Subsequence
}