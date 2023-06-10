/* Longest Common Subsequence Problem solution using recursion
Given two sequences, find the length of longest subsequence present in both of them.
A subsequence is a sequence that appears in the same relative order, but not necessarily contiguous. 

For example, “abc”,  “abg”, “bdf”, “aeg”,  ‘”acefg”, .. etc are subsequences of “abcdefg”.*/

#include<bits/stdc++.h>
using namespace std;

int lcs(string x,string y,int n,int m){

    if(n==0 || m==0){
        return  0;
    }
    if(x[n-1] == y[m-1]) {
        return 1 + lcs(x,y,n-1,m-1);   // 1 + lcs bcoz the last element was common from both strigs ri8,
    }          // it is a vaild ans so +1
    else if( x[n-1] != y[m-1]) {
        return max( lcs(x,y,n,m-1) , lcs(x,y,n-1,m));   // there are two possible ways to do it 
    } // in first recusive function we will shorten the last string and then proceed and we'll shorten the first string and the we'll proceed and 
    else // most important we'll take the max from them
        return 0;
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