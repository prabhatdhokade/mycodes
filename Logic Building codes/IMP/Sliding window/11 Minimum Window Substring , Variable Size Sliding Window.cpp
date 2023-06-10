/* 
HARD LEVEL 
Given two strings s and t, return the minimum window in s which will contain all the characters in t. If there is no such window in s that covers all characters in t, return the empty string "".

Note that If there is such a window, it is guaranteed that there will always be only one unique minimum window in s.

 

Example 1:

Input: s = "ADOBECODEBANC", t = "ABC"
Output: "BANC"
Example 2:

Input: s = "a", t = "a"
Output: "a"


TC : O(n+m)
SC : O(n+m)
*/
#include<bits/stdc++.h>

using namespace std;

string solve(string s1,string s2){
    string op="";
    if(s1.length() < s2.length()){
        return op;
    }
    
    unordered_map<char,int> m;   // usually take a unnorderd map
    for(int i=0;i<s2.length();i++){
        m[s2[i]]++;
    }

    int count = m.size();
    int i=0,j=0,ans = INT_MAX;

    while(j<s1.length()) {    // as usual

        if(m.find(s1[j]) != m.end()){   // if present in map then --
            m[s1[j]]--;
            if(m[s1[j]] == 0){
                count--;
            }
        }

        // else if ( count == 0) not working dont know why
        while(count == 0){    // this is little wanky,eat up heAD here
  
            if(ans > j-i+1){   // this is imp too
                ans = j-i+1;  // we have to only print the string only when the length is smaller
              op = s1.substr(i,j-i+1);   // ths is substring psuedo code
            }
            
            if(m.find(s1[i])!=m.end()){  
                m[s1[i]]++;
                if(m[s1[i]] > 0){
                    count++;
                }
            }
            i++;
        }
        j++;
    }
    return op;
}

int main()
{
    string s1,s2;
    cin>>s1>>s2;
    cout<< solve(s1,s2);
    
}
