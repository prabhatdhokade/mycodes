/* Minimum number of deletions and insertions to transform one string into another
Given two strings ‘str1’ and ‘str2’ of size m and n respectively. The task is to remove/delete and insert minimum number of characters from/in str1 so as to transform it into str2. It could be possible that the same character needs to be removed/deleted from one point of str1 and inserted to some another point.
Example:
Input : str1 = "geeksforgeeks", str2 = "geeks"
Output : Minimum Deletion = 8
         Minimum Insertion = 0 
*/

#include<bits/stdc++.h>

using namespace std;

int lcs(string s1,string s2,int n,int m) {
    int t[n+1][m+1];

    for(int i =0;i<n+1;i++) {
        for(int j=0;j<m+1;j++) {
            if ( i==0 || j==0) {
                t[i][j] =0;
            }
        }
    }
    for(int i=1;i<n+1;i++) {
        for(int j=1;j<m+1;j++){
            if(s1[i-1] == s2[j-1]) {
                t[i][j] = 1 + t[i-1][j-1];
            }
            else 
                t[i][j] = max (t[i][j-1] , t[i-1][j]);
        }
    }
    
    int ans = t[n][m];

    int de = s1.size() - ans; // for deletion,dont byheart just think about the solution
    int in = s2.size() - ans; // for insertion , just once think

    cout << de <<" "<< in ; // deletion ,insertaion
    return 1;
}


int main() 
{
    string s1;
    cin>>s1;
    string s2;
    cin>>s2;
    int n,m;
    n = s1.size();
    m = s2.size();

    lcs(s1,s2,n,m);

}